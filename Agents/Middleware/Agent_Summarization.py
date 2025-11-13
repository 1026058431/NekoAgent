"""Summarization middleware."""

import uuid
from collections.abc import Callable, Iterable
from typing import Any, cast

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    MessageLikeRepresentation,
    RemoveMessage,
    ToolMessage,
)
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langgraph.graph.message import (
    REMOVE_ALL_MESSAGES,
)
from langgraph.runtime import Runtime

from langchain.agents.middleware.types import AgentMiddleware, AgentState
from langchain.chat_models import BaseChatModel, init_chat_model

TokenCounter = Callable[[Iterable[MessageLikeRepresentation]], int]

DEFAULT_SUMMARY_PROMPT = """<role>
</role>

<primary_objective>
Your sole objective in this task is to extract the highest quality/most relevant context from the conversation history below.
</primary_objective>

<objective_information>
You're nearing the total number of input tokens you can accept, so you must extract the highest quality/most relevant pieces of information from your conversation history.
This context will then overwrite the conversation history presented below. Because of this, ensure the context you extract is only the most important information to your overall goal.
</objective_information>

<instructions>
The conversation history below will be replaced with the context you extract in this step. Because of this, you must do your very best to extract and record all of the most important context from the conversation history.
You want to ensure that you don't repeat any actions you've already completed, so the context you extract from the conversation history should be focused on the most important information to your overall goal.
</instructions>

The user will message you with the full message history you'll be extracting context from, to then replace. Carefully read over it all, and think deeply about what information is most important to your overall goal that should be saved:

With all of this in mind, please carefully read over the entire conversation history, and extract the most important and relevant context to replace it so that you can free up space in the conversation history.
Respond ONLY with the extracted context. Do not include any additional information, or text before or after the extracted context.

<messages>
Messages to summarize:
{messages}
</messages>"""  # noqa: E501

SUMMARY_PREFIX = "## Previous conversation summary:"

_DEFAULT_MESSAGES_TO_KEEP = 20
_DEFAULT_TRIM_TOKEN_LIMIT = 60000
_DEFAULT_FALLBACK_MESSAGE_COUNT = 15
_SEARCH_RANGE_FOR_TOOL_PAIRS = 5


class AgentSummarizationMiddleware(AgentMiddleware):
    """Summarizes conversation history when token limits are approached.

    This middleware monitors message token counts and automatically summarizes older
    messages when a threshold is reached, preserving recent messages and maintaining
    context continuity by ensuring AI/Tool message pairs remain together.
    """

    def __init__(
            self,
            model: str | BaseChatModel,
            max_tokens_before_summary: int | None = None,
            messages_to_keep: int = _DEFAULT_MESSAGES_TO_KEEP,
            token_counter: TokenCounter = count_tokens_approximately,
            summary_prompt: str = DEFAULT_SUMMARY_PROMPT,
            summary_prefix: str = SUMMARY_PREFIX,
            trim_token_limit: int = _DEFAULT_TRIM_TOKEN_LIMIT,  # 新增参数
            buffer_ratio: float = 0.3,  # 新增：缓冲区比例
    ) -> None:
        """Initialize the summarization middleware.

        Args:
            model: The language model to use for generating summaries.
            max_tokens_before_summary: Token threshold to trigger summarization.
                If `None`, summarization is disabled.
            messages_to_keep: Number of recent messages to preserve after summarization.
            token_counter: Function to count tokens in messages.
            summary_prompt: Prompt template for generating summaries.
            summary_prefix: Prefix added to system message when including summary.
            trim_token_limit: 截断消息最大长度限制，用于解决超长上下文IO时的问题。
            buffer_ratio: 缓冲区比例，用于确保总结后有足够的空间进行后续对话。
        """
        super().__init__()

        if isinstance(model, str):
            model = init_chat_model(model)

        self.model = model
        self.max_tokens_before_summary = max_tokens_before_summary
        self.messages_to_keep = messages_to_keep
        self.token_counter = token_counter
        self.summary_prompt = summary_prompt
        self.summary_prefix = summary_prefix
        self.trim_token_limit = trim_token_limit
        # 验证buffer_ratio在合理范围内
        if not 0 <= buffer_ratio <= 1:
            raise ValueError("buffer_ratio must be between 0 and 1")

        self.buffer_ratio = buffer_ratio

    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:  # noqa: ARG002
        """Process messages before model invocation, potentially triggering summarization."""
        messages = state["messages"]
        self._ensure_message_ids(messages)

        total_tokens = self.token_counter(messages)
        if (
            self.max_tokens_before_summary is not None
            and total_tokens < self.max_tokens_before_summary
        ):
            return None

        # 第一步：先找到安全的切割点（使用原来的逻辑）
        cutoff_index = self._find_safe_cutoff(messages)
        if cutoff_index <= 0:
            return None

        messages_to_summarize, preserved_messages = self._partition_messages(messages, cutoff_index)

        # 第二步：生成总结
        summary = self._create_summary(messages_to_summarize)

        # 第三步：计算总结后的token数，动态调整保留消息数量
        summary_tokens = self.token_counter([HumanMessage(content=summary)])
        available_for_preserved = self.max_tokens_before_summary - summary_tokens

        # 确保可用空间为正数
        if available_for_preserved <= 0:
            # 总结本身已经超过阈值，不保留任何原始消息
            adjusted_preserved_messages = []
        else:
            # 设置最小缓冲区（例如至少4000token）
            min_buffer = 4000
            buffer_tokens = max(
                min(
                    int(available_for_preserved * self.buffer_ratio),
                    available_for_preserved - min_buffer
                ),
                min_buffer  # 确保至少有最小缓冲区
            )
            final_available = available_for_preserved - buffer_tokens

            adjusted_preserved_messages = self._adjust_preserved_messages(
                preserved_messages, final_available
            )

        new_messages = self._build_new_messages(summary)

        return {
            "messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                *new_messages,
                *adjusted_preserved_messages,
            ]
        }

    def _adjust_preserved_messages(
            self,
            preserved_messages: list[AnyMessage],
            available_tokens: int
    ) -> list[AnyMessage]:
        """根据可用token数动态调整保留消息数量"""

        # 如果当前保留消息的token数在可用范围内，直接返回
        current_tokens = self.token_counter(preserved_messages)
        if current_tokens <= available_tokens:
            return preserved_messages

        # 添加调试信息
        original_count = len(preserved_messages)

        for reduced_count in range(len(preserved_messages), 0, -1):
            reduced_messages = preserved_messages[-reduced_count:]
            reduced_tokens = self.token_counter(reduced_messages)

            if reduced_tokens <= available_tokens:
                # 调试日志：记录调整情况
                # print(
                #     f"调整保留消息: {original_count} -> {reduced_count}, tokens: {current_tokens} -> {reduced_tokens}")
                return reduced_messages

        # 极端情况：即使保留1条消息也超限，返回空列表
        return []

    def _build_new_messages(self, summary: str) -> list[HumanMessage]:
        return [
            HumanMessage(content=f"以下是到目前为止的对话总结:\n\n{summary}")
        ]

    def _ensure_message_ids(self, messages: list[AnyMessage]) -> None:
        """Ensure all messages have unique IDs for the add_messages reducer."""
        for msg in messages:
            if msg.id is None:
                msg.id = str(uuid.uuid4())

    def _partition_messages(
        self,
        conversation_messages: list[AnyMessage],
        cutoff_index: int,
    ) -> tuple[list[AnyMessage], list[AnyMessage]]:
        """Partition messages into those to summarize and those to preserve."""
        messages_to_summarize = conversation_messages[:cutoff_index]
        preserved_messages = conversation_messages[cutoff_index:]

        return messages_to_summarize, preserved_messages

    def _find_safe_cutoff(self, messages: list[AnyMessage]) -> int:
        """Find safe cutoff point that preserves AI/Tool message pairs.

        Returns the index where messages can be safely cut without separating
        related AI and Tool messages. Returns 0 if no safe cutoff is found.
        """
        if len(messages) <= self.messages_to_keep:
            return 0

        target_cutoff = len(messages) - self.messages_to_keep

        for i in range(target_cutoff, -1, -1):
            if self._is_safe_cutoff_point(messages, i):
                return i

        return 0

    def _is_safe_cutoff_point(self, messages: list[AnyMessage], cutoff_index: int) -> bool:
        """Check if cutting at index would separate AI/Tool message pairs."""
        if cutoff_index >= len(messages):
            return True

        search_start = max(0, cutoff_index - _SEARCH_RANGE_FOR_TOOL_PAIRS)
        search_end = min(len(messages), cutoff_index + _SEARCH_RANGE_FOR_TOOL_PAIRS)

        for i in range(search_start, search_end):
            if not self._has_tool_calls(messages[i]):
                continue

            tool_call_ids = self._extract_tool_call_ids(cast("AIMessage", messages[i]))
            if self._cutoff_separates_tool_pair(messages, i, cutoff_index, tool_call_ids):
                return False

        return True

    def _has_tool_calls(self, message: AnyMessage) -> bool:
        """Check if message is an AI message with tool calls."""
        return (
            isinstance(message, AIMessage) and hasattr(message, "tool_calls") and message.tool_calls  # type: ignore[return-value]
        )

    def _extract_tool_call_ids(self, ai_message: AIMessage) -> set[str]:
        """Extract tool call IDs from an AI message."""
        tool_call_ids = set()
        for tc in ai_message.tool_calls:
            call_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
            if call_id is not None:
                tool_call_ids.add(call_id)
        return tool_call_ids

    def _cutoff_separates_tool_pair(
        self,
        messages: list[AnyMessage],
        ai_message_index: int,
        cutoff_index: int,
        tool_call_ids: set[str],
    ) -> bool:
        """Check if cutoff separates an AI message from its corresponding tool messages."""
        for j in range(ai_message_index + 1, len(messages)):
            message = messages[j]
            if isinstance(message, ToolMessage) and message.tool_call_id in tool_call_ids:
                ai_before_cutoff = ai_message_index < cutoff_index
                tool_before_cutoff = j < cutoff_index
                if ai_before_cutoff != tool_before_cutoff:
                    return True
        return False

    def _create_summary(self, messages_to_summarize: list[AnyMessage]) -> str:
        """Generate summary for the given messages."""
        if not messages_to_summarize:
            return "No previous conversation history."

        trimmed_messages = self._trim_messages_for_summary(messages_to_summarize)
        if not trimmed_messages:
            return "Previous conversation was too long to summarize."

        try:
            response = self.model.invoke(self.summary_prompt.format(messages=trimmed_messages))
            return cast("str", response.content).strip()
        except Exception as e:  # noqa: BLE001
            return f"Error generating summary: {e!s}"

    def _trim_messages_for_summary(self, messages: list[AnyMessage]) -> list[AnyMessage]:
        """改进的trim策略，确保永不返回空列表"""
        try:
            trimmed = trim_messages(
                messages,
                max_tokens=self.trim_token_limit,
                token_counter=self.token_counter,
                start_on="human",
                strategy="last",
                allow_partial=True,
                include_system=True,
            )

            # 确保trimmed不为空
            if not trimmed and messages:
                # 即使单条消息超过限制，也要保留最后1条
                return messages[-1:]

            return trimmed

        except Exception:
            # 异常时也确保返回一些消息
            fallback_count = min(_DEFAULT_FALLBACK_MESSAGE_COUNT, len(messages))
            return messages[-fallback_count:]
