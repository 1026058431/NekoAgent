# LangChain 运行时指南

## 概述

LangChain 的 `create_agent` 在底层运行在 LangGraph 的运行时上。LangGraph 公开了一个 Runtime 对象，包含以下信息：

- **Context**：静态信息，如用户 ID、数据库连接或其他智能体调用的依赖项
- **Store**：用于长期记忆的 BaseStore 实例
- **Stream writer**：用于通过 "custom" 流模式流式传输信息的对象

您可以在工具和中间件中访问运行时信息。

## 访问

当使用 `create_agent` 创建智能体时，您可以指定 `context_schema` 来定义存储在智能体 Runtime 中的上下文结构。

在调用智能体时，传递 `context` 参数以及运行的相关配置：

```python
from dataclasses import dataclass
from langchain.agents import create_agent

@dataclass
class Context:
    user_name: str

agent = create_agent(
    model="gpt-5-nano",
    tools=[...],
    context_schema=Context
)

agent.invoke({
    "messages": [{"role": "user", "content": "What's my name?"}],
    context=Context(user_name="John Smith")
})
```

## 在工具内部

您可以在工具内部访问运行时信息以：
- 访问上下文
- 读取或写入长期记忆
- 写入自定义流（例如，工具进度更新）

使用 `ToolRuntime` 参数在工具内部访问 Runtime 对象。

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class Context:
    user_id: str

@tool
def fetch_user_email_preferences(runtime: ToolRuntime[Context]) -> str:
    """Fetch the user's email preferences from the store."""
    user_id = runtime.context.user_id
    
    preferences: str = "The user prefers you to write a brief and polite email."
    
    if runtime.store:
        if memory := runtime.store.get(("users",), user_id):
            preferences = memory.value["preferences"]
    
    return preferences
```

## 在中间件内部

您可以在中间件中访问运行时信息以创建动态提示、修改消息或基于用户上下文控制智能体行为。

使用 `request.runtime` 在中间件装饰器内部访问 Runtime 对象。运行时对象在传递给中间件函数的 `ModelRequest` 参数中可用。

```python
from dataclasses import dataclass
from langchain.messages import AnyMessage
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model
from langgraph.runtime import Runtime

@dataclass
class Context:
    user_name: str

# 动态提示
@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest[Context]) -> str:
    user_name = request.runtime.context.user_name
    system_prompt = f"You are a helpful assistant. Address the user as {user_name}."
    return system_prompt

# 模型前钩子
@before_model
def log_before_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"Processing request for user: {runtime.context.user_name}")
    return None

# 模型后钩子
@after_model
def log_after_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"Completed request for user: {runtime.context.user_name}")
    return None

agent = create_agent(
    model="gpt-5-nano",
    tools=[...],
    middleware=[dynamic_system_prompt, log_before_model, log_after_model],
    context_schema=Context
)

agent.invoke({
    "messages": [{"role": "user", "content": "What's my name?"}],
    context=Context(user_name="John Smith")
})
```

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/runtime