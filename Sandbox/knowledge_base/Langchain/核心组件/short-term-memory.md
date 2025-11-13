# LangChain 短期记忆指南

## 概述

记忆是一个记住先前交互信息的系统。对于 AI 智能体来说，记忆至关重要，因为它让它们能够记住先前的交互、从反馈中学习并适应用户偏好。随着智能体处理具有众多用户交互的更复杂任务，这种能力对于效率和用户满意度都变得至关重要。

短期记忆让您的应用程序能够在单个线程或对话中记住先前的交互。线程在一个会话中组织多个交互，类似于电子邮件在单个对话中分组消息的方式。

对话历史是短期记忆的最常见形式。长对话对当今的 LLM 构成了挑战；完整的历史可能不适合 LLM 的上下文窗口，导致上下文丢失或错误。即使您的模型支持完整的上下文长度，大多数 LLM 在长上下文上的表现仍然很差。它们会被陈旧或离题的内容分散注意力，同时遭受较慢的响应时间和更高的成本。

## 用法

要向智能体添加短期记忆（线程级持久性），您需要在创建智能体时指定一个检查点器。LangChain 的智能体将短期记忆作为智能体状态的一部分进行管理。通过将这些存储在图形状态中，智能体可以访问给定对话的完整上下文，同时保持不同线程之间的分离。

状态使用检查点器持久化到数据库（或内存）中，因此线程可以在任何时候恢复。短期记忆在调用智能体或完成步骤（如工具调用）时更新，状态在每个步骤开始时读取。

```python
from langchain.agents import create_agent
from langgraph.memory import InMemorySaver

agent = create_agent(
    "gpt-5",
    [get_user_info],
    checkpointer=InMemorySaver(),
)

agent.invoke({
    "messages": [{"role": "user", "content": "Hi."}],
    "configurable": {"thread_id": "1"}
})
```

## 生产环境

在生产环境中，使用由数据库支持的检查点器：

```python
pip install langgraph-checkpoint-postgres
```

```python
from langchain.agents import create_agent
from langgraph.postgres import PostgresSaver

DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()  # 在 Postgres 中自动创建表
    
    agent = create_agent(
        "gpt-5",
        [get_user_info],
        checkpointer=checkpointer,
    )
```

## 自定义智能体记忆

默认情况下，智能体使用 `AgentState` 来管理短期记忆，特别是通过 `messages` 键的对话历史。您可以扩展 `AgentState` 以添加其他字段。自定义状态模式使用 `state_schema` 参数传递给 `create_agent`。

```python
from langchain.agents import create_agent, AgentState
from langgraph.memory import InMemorySaver

class CustomAgentState(AgentState):
    user_id: str
    preferences: dict

agent = create_agent(
    "gpt-5",
    [get_user_info],
    state_schema=CustomAgentState,
    checkpointer=InMemorySaver(),
)

# 自定义状态可以在调用中传递
result = agent.invoke({
    "messages": [{"role": "user", "content": "Hello"}],
    "user_id": "user_123",
    "preferences": {"theme": "dark"}
}, {"configurable": {"thread_id": "1"}})
```

## 常见模式

启用短期记忆后，长对话可能超过 LLM 的上下文窗口。常见的解决方案是：

- **修剪消息** - 删除前 N 个或后 N 个消息（在调用 LLM 之前）
- **删除消息** - 从 LangGraph 状态中永久删除消息
- **总结消息** - 总结历史中的早期消息并用摘要替换它们
- **自定义策略** - 自定义策略（例如，消息过滤等）

这允许智能体跟踪对话而不会超过 LLM 的上下文窗口。

### 修剪消息

大多数 LLM 都有最大支持的上下文窗口（以令牌为单位）。决定何时截断消息的一种方法是计算消息历史中的令牌数，并在接近该限制时截断。

如果您使用 LangChain，可以使用修剪消息实用程序并指定要从列表中保留的令牌数，以及用于处理边界的策略（例如，保留最后 `max_tokens`）。

要在智能体中修剪消息历史，请使用 `before_model` 中间件装饰器：

```python
from langchain.messages import RemoveMessage
from langgraph.message import REMOVE_ALL_MESSAGES
from langgraph.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.middleware import before_model
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig

@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    messages = state["messages"]
    if len(messages) > 2:
        # 删除最早的两个消息
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return None

agent = create_agent(
    "gpt-5-nano",
    tools,
    system_prompt="Please be concise and to the point.",
    middleware=[trim_messages],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

agent.invoke({"messages": [{"role": "user", "content": "hi, my name is bob"}]}, config)
agent.invoke({"messages": [{"role": "user", "content": "write a short poem about cats"}]}, config)
agent.invoke({"messages": [{"role": "user", "content": "now do the same but for dogs"}]}, config)

final_response = agent.invoke({"messages": [{"role": "user", "content": "what's my name?"}]}, config)
print(final_response["messages"][-1].pretty_print())
```

### 删除消息

您可以从图形状态中删除消息以管理消息历史。这在您想要删除特定消息或清除整个消息历史时很有用。

要从图形状态中删除消息，可以使用 `RemoveMessage`。默认的 `AgentState` 提供了这个功能。

**删除特定消息**
```python
from langchain.messages import RemoveMessage

def delete_messages(state):
    messages = state["messages"]
    if len(messages) > 2:
        # 删除最早的两个消息
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
```

**删除所有消息**
```python
from langgraph.message import REMOVE_ALL_MESSAGES

def delete_messages(state):
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]}
```

删除消息时，请确保生成的消息历史是有效的。检查您使用的 LLM 提供商的限制。

### 总结消息

如上所示，修剪或删除消息的问题在于您可能会因消息队列的删减而丢失信息。因此，一些应用程序受益于使用聊天模型总结消息历史的更复杂方法。

要在智能体中总结消息历史，请使用内置的 `SummarizationMiddleware`：

```python
from langchain.agents import create_agent
from langchain.middleware import SummarizationMiddleware
from langgraph.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

agent = create_agent(
    "gpt-5-nano",
    tools,
    middleware=[SummarizationMiddleware()],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

agent.invoke({"messages": [{"role": "user", "content": "hi, my name is bob"}]}, config)
agent.invoke({"messages": [{"role": "user", "content": "write a short poem about cats"}]}, config)
agent.invoke({"messages": [{"role": "user", "content": "now do the same but for dogs"}]}, config)

final_response = agent.invoke({"messages": [{"role": "user", "content": "what's my name?"}]}, config)
print(final_response["messages"][-1].pretty_print())
```

## 工具

### 在工具中读取短期记忆

要从工具访问智能体的状态，请使用 `ToolRuntime`。`tool_runtime` 参数从工具签名中隐藏（因此模型看不到它），但工具可以通过它访问状态。

```python
from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime

class CustomState(AgentState):
    user_id: str

@tool
def get_user_info(runtime: ToolRuntime) -> str:
    """Look up user info."""
    user_id = runtime.state["user_id"]
    return "User is John Smith" if user_id == "user_123" else "Unknown user"

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_user_info],
    state_schema=CustomState,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "look up user information"}],
    "user_id": "user_123"
})

print(result["messages"][-1].content)  # "User is John Smith."
```

### 从工具写入短期记忆

要在执行期间修改智能体的短期记忆（状态），您可以直接从工具返回状态更新。这对于持久化中间结果或使信息可供后续工具或提示访问很有用。

```python
from langchain.tools import tool, ToolRuntime
from langchain_core.runnables import RunnableConfig
from langchain.messages import ToolMessage
from langchain.agents import create_agent, AgentState
from langgraph.memory import InMemorySaver

class CustomState(AgentState):
    user_name: str

@tool
def update_user_info(runtime: ToolRuntime) -> str:
    """Update user information."""
    user_name = "John Smith"
    
    # 更新状态
    runtime.state["user_name"] = user_name
    
    return ToolMessage(
        content=f"Updated user info: {user_name}",
        tool_call_id=runtime.tool_call_id
    )

@tool
def greet(runtime: ToolRuntime) -> str:
    """Use this to greet the user once you found their info."""
    user_name = runtime.state["user_name"]
    return f"Hello {user_name}!"

agent = create_agent(
    model="gpt-5-nano",
    tools=[update_user_info, greet],
    state_schema=CustomState,
    checkpointer=InMemorySaver(),
)
```

## 提示

### 动态提示

您可以使用 `dynamic_prompt` 中间件基于上下文动态生成系统提示。

```python
from langchain.agents import create_agent
from typing import TypedDict
from langchain.middleware import dynamic_prompt, ModelRequest

class CustomContext(TypedDict):
    user_name: str

def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is always sunny."

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.context["user_name"]
    system_prompt = f"You are a helpful assistant. Address the user as {user_name}."
    return system_prompt

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
    middleware=[dynamic_system_prompt],
    context_schema=CustomContext,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What is the weather in SF?"}],
    "context": CustomContext(user_name="John Smith")
})

for msg in result["messages"]:
    msg.pretty_print()
```

## 模型前后

### 模型前

在 `before_model` 中间件中访问短期记忆（状态）以在模型调用之前处理消息。

```python
from langchain.messages import RemoveMessage
from langgraph.message import REMOVE_ALL_MESSAGES
from langgraph.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.middleware import before_model
from langgraph.runtime import Runtime
from typing import Any

@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    messages = state["messages"]
    if len(messages) > 2:
        # 删除最早的两个消息
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return None
```

### 模型后

在 `after_model` 中间件中访问短期记忆（状态）以在模型调用之后处理消息。

```python
from langchain.messages import RemoveMessage
from langgraph.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.middleware import after_model
from langgraph.runtime import Runtime

@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove messages containing sensitive words."""
    STOP_WORDS = ["password", "secret"]
    last_message = state["messages"][-1]
    if any(word in last_message.content for word in STOP_WORDS):
        return {"messages": [RemoveMessage(id=last_message.id)]}
    return None

agent = create_agent(
    model="gpt-5-nano",
    tools=[],
    middleware=[validate_response],
    checkpointer=InMemorySaver(),
)
```

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/short-term-memory