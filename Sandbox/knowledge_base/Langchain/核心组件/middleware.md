# LangChain 中间件指南

## 概述

中间件提供了一种更紧密地控制智能体内部发生情况的方式。

## 中间件能做什么？

中间件可以在智能体执行的各个阶段插入自定义逻辑：
- 在模型调用之前和之后
- 在工具执行期间
- 在智能体开始和结束时
- 动态修改提示、状态或响应

## 内置中间件

### 总结中间件

自动总结对话历史以保持在上下文窗口限制内。

**适用场景：**
- 超过上下文窗口的长对话
- 具有广泛历史的多轮对话
- 需要保留完整对话上下文的应用

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[weather_tool, calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-4o-mini",
            max_tokens_before_summary=4000,  # 在4000个token时触发总结
            messages_to_keep=20,  # 总结后保留最近20条消息
            summary_prompt="Custom prompt for summarization...",  # 可选
        ),
    ],
)
```

**配置选项：**
- `model` (string, required) - 用于生成总结的模型
- `max_tokens_before_summary` (number) - 触发总结的token阈值
- `messages_to_keep` (number, default: 20) - 要保留的最近消息数
- `token_counter` (function) - 自定义token计数函数。默认为基于字符的计数。
- `summary_prompt` (string) - 自定义提示模板。如果未指定，使用内置模板。
- `summary_prefix` (string, default: "## Previous conversation summary:") - 总结消息的前缀

### 人工干预中间件

在敏感操作之前暂停执行以获取人工批准。

**适用场景：**
- 高风险操作（删除、支付、数据修改）
- 需要人工监督的敏感任务
- 合规和审计要求

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="gpt-4o",
    tools=[read_email_tool, send_email_tool],
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # 发送邮件需要批准、编辑或拒绝
                "send_email_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                # 自动批准读取邮件
                "read_email_tool": False,
            }
        ),
    ],
)
```

**配置选项：**
- `interrupt_on` (dict, required) - 工具名称到批准配置的映射。值可以是 True（使用默认配置中断）、False（自动批准）或 InterruptOnConfig 对象。
- `description_prefix` (string, default: "Tool execution requires approval") - 操作请求描述的前缀

**InterruptOnConfig 选项：**
- `allowed_decisions` (list[string]) - 允许的决策列表："approve"、"edit" 或 "reject"
- `description` (string | callable) - 静态字符串或用于自定义描述的可调用函数

**重要提示：** 人工干预中间件需要检查点器来在中断之间维护状态。

### Anthropic 提示缓存

通过缓存重复的提示前缀来减少 Anthropic 模型的成本。

```python
from langchain_anthropic import ChatAnthropic
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langchain.agents import create_agent

LONG_PROMPT = """
Please be a helpful assistant.
<Lots more context ...>
"""

agent = create_agent(
    model=ChatAnthropic(model="claude-sonnet-4-5-20250929"),
    system_prompt=LONG_PROMPT,
    middleware=[AnthropicPromptCachingMiddleware(ttl="5m")],
)

# 缓存存储
agent.invoke({"messages": [HumanMessage("Hi, my name is Bob")]})

# 缓存命中，系统提示被缓存
agent.invoke({"messages": [HumanMessage("What's my name?")]})
```

**配置选项：**
- `type` (string, default: "ephemeral") - 缓存类型。目前仅支持 "ephemeral"。
- `ttl` (string, default: "5m") - 缓存内容的生存时间。有效值："5m" 或 "1h"。
- `min_messages_to_cache` (number, default: 0) - 缓存开始前的最小消息数。
- `unsupported_model_behavior` (string, default: "warn") - 使用非 Anthropic 模型时的行为。选项："ignore"、"warn" 或 "raise"。

### 模型调用限制

限制模型调用次数以防止无限循环或过度成本。

**适用场景：**
- 防止失控智能体进行过多 API 调用
- 在生产部署中强制执行成本控制
- 在特定调用预算内测试智能体行为

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=10,  # 每个线程最多10次调用（跨运行）
            run_limit=5,     # 每次运行最多5次调用（单次调用）
            exit_behavior="end",  # 或 "error" 引发异常
        ),
    ],
)
```

**配置选项：**
- `thread_limit` (number) - 线程中所有运行的最大模型调用次数。默认为无限制。
- `run_limit` (number) - 单次调用的最大模型调用次数。默认为无限制。
- `exit_behavior` (string, default: "end") - 达到限制时的行为。选项："end"（优雅终止）或 "error"（引发异常）。

### 工具调用限制

限制特定工具或所有工具的调用次数。

**适用场景：**
- 防止对昂贵外部 API 的过多调用
- 限制网络搜索或数据库查询
- 对特定工具使用强制执行速率限制

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware

# 全局限制：每个线程最多20次调用，每次运行10次
global_limiter = ToolCallLimitMiddleware(
    thread_limit=20,
    run_limit=10,
)

# 特定工具限制，使用默认 "continue" 行为
search_limiter = ToolCallLimitMiddleware(
    tool_name="search",
    thread_limit=5,
    run_limit=3,
)

# 仅线程限制（无每次运行限制）
database_limiter = ToolCallLimitMiddleware(
    tool_name="query_database",
    thread_limit=10,
)

# 使用 "error" 行为的严格强制执行
web_scraper_limiter = ToolCallLimitMiddleware(
    tool_name="scrape_webpage",
    run_limit=2,
    exit_behavior="error",
)

# 使用 "end" 行为的立即终止
critical_tool_limiter = ToolCallLimitMiddleware(
    tool_name="delete_records",
    run_limit=1,
    exit_behavior="end",
)

# 一起使用多个限制器
agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, database_tool, scraper_tool],
    middleware=[
        global_limiter,
        search_limiter,
        database_limiter,
        web_scraper_limiter
    ],
)
```

**配置选项：**
- `tool_name` (string) - 要限制的特定工具名称。如果未提供，限制适用于所有工具全局。
- `thread_limit` (number) - 线程中所有运行的最大工具调用次数。在具有相同线程 ID 的多个调用之间持久化。需要检查点器来维护状态。None 表示无线程限制。
- `run_limit` (number) - 单次调用的最大工具调用次数（一个用户消息 → 响应周期）。每次新用户消息时重置。None 表示无运行限制。
- `exit_behavior` (string, default: "continue") - 达到限制时的行为：
  - "continue"（默认）- 阻止超出的工具调用并显示错误消息，让其他工具和模型继续。模型根据错误消息决定何时结束。
  - "error" - 立即引发 ToolCallLimitExceededError 异常，停止执行
  - "end" - 立即停止执行，为超出的工具调用提供 ToolMessage 和 AI 消息。仅在限制单个工具时有效；如果其他工具有待处理调用，则引发 NotImplementedError

**注意：** 必须指定 thread_limit 或 run_limit 中的至少一个。

### 模型回退

当主模型失败时自动回退到替代模型。

**适用场景：**
- 构建能够处理模型中断的弹性智能体
- 通过回退到更便宜的模型进行成本优化
- 跨 OpenAI、Anthropic 等的提供商冗余

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(
    model="gpt-4o",  # 主模型
    tools=[...],
    middleware=[
        ModelFallbackMiddleware(
            "gpt-4o-mini",  # 出错时首先尝试
            "claude-3-5-sonnet-20241022",  # 然后这个
        ),
    ],
)
```

**配置选项：**
- `first_model` (string | BaseChatModel, required) - 当主模型失败时首先尝试的回退模型。可以是模型字符串（例如 "openai:gpt-4o-mini"）或 BaseChatModel 实例。
- `*additional_models` (string | BaseChatModel) - 如果先前模型失败，按顺序尝试的额外回退模型

### PII 检测

检测和处理对话中的个人身份信息。

**适用场景：**
- 具有合规要求的医疗和金融应用
- 需要清理日志的客户服务智能体
- 处理敏感用户数据的任何应用

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[
        # 在用户输入中编辑电子邮件
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        # 屏蔽信用卡（显示最后4位）
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
        # 带有正则表达式的自定义 PII 类型
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",  # 如果检测到则引发错误
        ),
    ],
)
```

**配置选项：**
- `pii_type` (string, required) - 要检测的 PII 类型。可以是内置类型（email、credit_card、ip、mac_address、url）或自定义类型名称。
- `strategy` (string, default: "redact") - 如何处理检测到的 PII。选项："block" - 检测到时引发异常；"redact" - 替换为 [REDACTED_TYPE]；"mask" - 部分屏蔽（例如，****-****-****-1234）；"hash" - 替换为确定性哈希。
- `detector` (function | regex) - 自定义检测器函数或正则表达式模式。如果未提供，使用该 PII 类型的内置检测器。
- `apply_to_input` (boolean, default: True) - 在模型调用之前检查用户消息
- `apply_to_output` (boolean, default: False) - 在模型调用之后检查 AI 消息
- `apply_to_tool_results` (boolean, default: False) - 在执行之后检查工具结果消息

### 待办事项列表

为智能体配备任务规划和跟踪功能，用于复杂的多步骤任务。

**适用场景：**
- 需要跨多个工具协调的复杂多步骤任务
- 需要进度可见性的长时间运行操作

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

@tool
def read_file(file_path: str) -> str:
    """Read contents of a file."""
    with open(file_path) as f:
        return f.read()

@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file."""
    with open(file_path, 'w') as f:
        f.write(content)
    return f"Wrote {len(content)} characters to {file_path}"

@tool
def run_tests(test_path: str) -> str:
    """Run tests and return results."""
    # 简化示例
    return "All tests passed!"

agent = create_agent(
    model="gpt-4o",
    tools=[read_file, write_file, run_tests],
    middleware=[TodoListMiddleware()],
)

result = agent.invoke({
    "messages": [HumanMessage("Refactor the authentication module to use async/await and ensure all tests pass")]
})

# 智能体将使用 write_todos 来规划和跟踪：
# 1. 读取当前认证模块代码
# 2. 识别需要异步转换的函数
# 3. 将函数重构为 async/await
# 4. 在整个代码库中更新函数调用
# 5. 运行测试并修复任何失败

print(result["todos"])  # 跟踪智能体在每个步骤中的进度
```

**配置选项：**
- `system_prompt` (string) - 指导待办事项使用的自定义系统提示。如果未指定，使用内置提示。
- `tool_description` (string) - `write_todos` 工具的自定义描述。如果未指定，使用内置描述。

### LLM 工具选择器

在调用主模型之前使用 LLM 智能选择相关工具。

**适用场景：**
- 具有许多工具（10+）的智能体，其中大多数与每个查询无关
- 通过过滤不相关工具减少令牌使用
- 提高模型专注度和准确性

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[tool1, tool2, tool3, tool4, tool5, ...],
    middleware=[LLMToolSelectorMiddleware()],
)
```

**配置选项：**
- `model` (string | BaseChatModel) - 用于工具选择的模型。可以是模型字符串或 BaseChatModel 实例。默认为智能体的主模型。
- `system_prompt` (string) - 选择模型的指令。如果未指定，使用内置提示。
- `max_tools` (number) - 要选择的最大工具数。默认为无限制。
- `always_include` (list[string]) - 始终包含在选择中的工具名称列表。

### 工具重试

使用可配置的指数退避自动重试失败的工具调用。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, database_tool],
    middleware=[
        ToolRetryMiddleware(
            max_retries=3,  # 最多重试3次
            backoff_factor=2.0,  # 指数退避乘数
            initial_delay=1.0,  # 从1秒延迟开始
            max_delay=60.0,  # 最大延迟60秒
        )
    ],
)
```

**配置选项：**
- `**配置选项：**
- `tool_names` (list[string]) - 要应用重试的工具名称列表。如果为 None，应用于所有工具。
- `max_retries` (number) - 最大重试次数。
- `retry_on` (tuple[type[Exception], ...] | callable, default: (Exception,)) - 要重试的异常类型元组，或接受异常并在应重试时返回 True 的可调用对象。
- `on_failure` (string | callable, default: "return_message") - 所有重试耗尽时的行为。
- `backoff_factor` (number, default: 2.0) - 指数退避的乘数。每次重试等待 `initial_delay * (backoff_factor ^ retry_number)` 秒。设置为 1.0 用于恒定延迟。
- `initial_delay` (number, default: 1.0) - 第一次重试前的初始延迟（秒）。
- `max_delay` (number, default: 60.0) - 最大延迟（秒）。

### LLM 工具模拟器

使用 LLM 模拟工具执行而不是实际调用工具。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulatorMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, database_tool],
    middleware=[
        LLMToolEmulatorMiddleware(
            tool_names=["search_tool"],  # 仅模拟搜索工具
            model="anthropic:claude-3-5-sonnet-latest"
        )
    ],
)
```

**配置选项：**
- `tool_names` (list[string]) - 要模拟的工具名称列表。如果为 None（默认），所有工具都将被模拟。如果为空列表，没有工具将被模拟。
- `model` (string | BaseChatModel, default: "anthropic:claude-3-5-sonnet-latest") - 用于生成模拟工具响应的模型。

### 上下文编辑

通过修剪、总结或清除工具使用来管理对话上下文。

**适用场景：**
- 需要定期上下文清理的长对话
- 从上下文中删除失败的工具尝试
- 自定义上下文管理策略

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[ContextEditingMiddleware(edits=[ClearToolUsesEdit()])],
)
```

## 自定义中间件

### 装饰器基础中间件

**可用装饰器：**
- `@before_model` - 在每个模型调用之前运行
- `@after_model` - 在每个模型响应之后运行
- `@wrap_model_call` - 包装模型调用处理程序
- `@dynamic_prompt` - 动态生成系统提示

**何时使用装饰器：**
- 简单的单功能中间件
- 不需要复杂状态管理的逻辑
- 快速原型和实验

```python
from langchain.agents.middleware import before_model, after_model, wrap_model_call
from langchain.agents.middleware import AgentState, ModelRequest, ModelResponse, dynamic_prompt
from langchain_core.messages import AIMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

@before_model
def log_before_model(state: AgentState) -> None:
    """Log before each model call."""
    print(f"Model call with {len(state['messages'])} messages")

@after_model
def validate_output(state: AgentState) -> dict | None:
    """Validate model output."""
    last_message = state["messages"][-1]
    if "sorry" in last_message.content.lower():
        return {"messages": [AIMessage("I cannot respond to that request.")]}
    return None

@wrap_model_call
def retry_model(handler, request: ModelRequest) -> ModelResponse:
    """Retry model calls on failure."""
    for attempt in range(3):
        try:
            return handler(request)
        except Exception as e:
            if attempt == 2:
                raise e
            print(f"Retry {attempt + 1} after error: {e}")

@dynamic_prompt
def personalized_prompt(request: ModelRequest) -> str:
    """Generate personalized system prompt."""
    user_id = request.state.get("user_id", "guest")
    return f"You are a helpful assistant for user {user_id}. Be concise and friendly."

# 在智能体中使用装饰器
agent = create_agent(
    model="gpt-4o",
    middleware=[log_before_model, validate_output, retry_model, personalized_prompt],
    tools=[],
    checkpointer=InMemorySaver(),
)
```

### 类基础中间件

**两种钩子样式：**

**节点样式钩子**
在执行流程的特定点运行：
- `before_agent` - 在智能体开始之前（每次调用一次）
- `before_model` - 在每个模型调用之前
- `after_model` - 在每个模型响应之后
- `after_agent` - 在智能体完成后（最多每次调用一次）

**使用场景：** 日志记录、验证和状态更新。

**包装样式钩子**
拦截执行，完全控制处理程序调用。

**使用场景：** 重试、缓存和转换。

```python
from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any

class MessageLimitMiddleware(AgentMiddleware):
    def __init__(self, max_messages: int = 50):
        super().__init__()
        self.max_messages = max_messages
    
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # 检查消息数量
        if len(state["messages"]) >= self.max_messages:
            return {
                "messages": [AIMessage("Conversation limit reached. Please start a new conversation.")],
                "jump_to": "end"
            }
        return None

class LoggingMiddleware(AgentMiddleware):
    def before_model(self, state: AgentState, runtime: Runtime) -> None:
        print(f"Model call with {len(state['messages'])} messages")
    
    def after_model(self, state: AgentState, runtime: Runtime) -> None:
        last_message = state["messages"][-1]
        print(f"Model response: {last_message.content[:100]}...")

# 使用自定义中间件
agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[MessageLimitMiddleware(max_messages=50), LoggingMiddleware()],
)
```

### 自定义状态模式

中间件可以定义和访问自定义状态属性：

```python
from langchain.agents.middleware import AgentMiddleware, AgentState
from typing import Any

class UserTrackingMiddleware(AgentMiddleware):
    def __init__(self):
        super().__init__()
        
    def before_agent(self, state: AgentState, runtime: Runtime) -> None:
        # 初始化自定义状态
        if "user_id" not in state:
            state["user_id"] = "guest"
        if "model_call_count" not in state:
            state["model_call_count"] = 0
    
    def before_model(self, state: AgentState, runtime: Runtime) -> None:
        # 更新自定义状态
        state["model_call_count"] += 1

# 使用自定义状态
agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[UserTrackingMiddleware()],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Hello"}],
    "model_call_count": 0,
    "user_id": "user-123",
})
```

### 执行顺序

当使用多个中间件时，理解执行顺序很重要：

```python
agent = create_agent(
    model="gpt-4o",
    middleware=[middleware1, middleware2, middleware3],
    tools=[...],
)
```

**执行顺序：**
- `before_agent()`: middleware1 → middleware2 → middleware3
- `before_model()`: middleware1 → middleware2 → middleware3
- `after_model()`: middleware3 → middleware2 → middleware1
- `after_agent()`: middleware3 → middleware2 → middleware1

**关键规则：**
- `before_` 钩子：从第一个到最后一个
- `after_` 钩子：从最后一个到第一个（反向）
- `wrap_` 钩子：嵌套（第一个中间件包装所有其他）

### 智能体跳转

要从中间件提前退出，返回带有 `jump_to` 的字典：

```python
class EarlyExitMiddleware(AgentMiddleware):
    def before_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        # 检查某些条件
        if should_exit(state):
            return {
                "messages": [AIMessage("Exiting early due to condition.")],
                "jump_to": "end"
            }
        return None
```

**可用跳转目标：**
- `"end"`: 跳转到智能体执行结束
- `"tools"`: 跳转到工具节点
- `"model"`: 跳转到模型节点（或第一个 before_model 钩子）

**重要提示：** 当从 before_model 或 after_model 跳转时，跳转到 "model" 将导致所有 before_model 中间件再次运行。

```python
from langchain.agents.middleware import AgentMiddleware, hook_config
from typing import Any

class ConditionalMiddleware(AgentMiddleware):
    @hook_config(can_jump_to=["end", "tools"])
    def after_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        if some_condition(state):
            return {"jump_to": "end"}
        return None
```

## 最佳实践

- **保持中间件专注** - 每个中间件应该做好一件事
- **优雅处理错误** - 不要让中间件错误使智能体崩溃
- **使用适当的钩子类型**：
  - 节点样式用于顺序逻辑（日志记录、验证）
  - 包装样式用于控制流（重试、回退、缓存）
- **清晰记录任何自定义状态属性**
- **在集成之前独立单元测试中间件**
- **考虑执行顺序** - 将关键中间件放在列表首位
- **尽可能使用内置中间件**，不要重新发明轮子 :)

## 示例

### 动态选择工具

在运行时选择相关工具以提高性能和准确性。

```python
from dataclasses import dataclass
from typing import Literal, Callable
from langchain.agents.middleware import LLMToolSelectorMiddleware

@dataclass
class Context:
    provider: Literal["github", "gitlab"]
    
class ContextAwareToolSelector(LLMToolSelectorMiddleware):
    def __init__(self, context_schema: Callable):
        super().__init__()
        self.context_schema = context_schema
    
    def select_tools(self, state: AgentState) -> list[str]:
        context = state.get("context")
        if context and context.provider == "github":
            return ["github_create_issue", "github_search_issues"]
        elif context and context.provider == "gitlab":
            return ["gitlab_create_issue", "gitlab_search_issues"]
        return super().select_tools(state)

# 注册所有工具
agent = create_agent(
    model="gpt-4o",
    tools=[github_create_issue, github_search_issues, gitlab_create_issue, gitlab_search_issues],
    middleware=[ContextAwareToolSelector(context_schema=Context)],
)

# 使用上下文调用
result = agent.invoke({
    "messages": [{"role": "user", "content": "Open an issue titled 'Bug: where are the cats' in the repository its-a-cats-game"}],
    "context": Context(provider="github"),
})
```

**关键点：**
- 预先注册所有工具
- 中间件根据请求选择相关子集
- 使用 context_schema 进行配置要求

## 其他资源

- 中间件 API 参考 - 自定义中间件的完整指南
- 人工干预 - 为敏感操作添加人工审查
- 测试智能体 - 测试安全机制的策略

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/middleware