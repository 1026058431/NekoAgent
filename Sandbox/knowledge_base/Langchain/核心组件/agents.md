# LangChain 智能体

## 智能体概述

LangChain 智能体是能够使用工具来执行任务的 AI 系统。它们基于 LangGraph 构建，提供持久执行、流式传输、人工干预、持久化等功能。

## 创建智能体

### 基础智能体创建

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)
```

### 高级智能体配置

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver

# 定义上下文模式
@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str

# 定义工具
@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"

# 配置模型
model = init_chat_model(
    "claude-sonnet-4-5-20250929",
    temperature=0
)

# 定义响应格式
@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    punny_response: str
    weather_conditions: str | None = None

# 设置记忆
checkpointer = InMemorySaver()

# 创建智能体
agent = create_agent(
    model=model,
    system_prompt="You are an expert weather forecaster",
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ResponseFormat,
    checkpointer=checkpointer
)
```

## 智能体特性

### 1. 工具使用

智能体可以调用外部工具来获取信息或执行操作：

```python
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"

@tool
def calculate_math(expression: str) -> str:
    """Calculate mathematical expressions."""
    return str(eval(expression))
```

### 2. 上下文感知

智能体可以访问运行时上下文：

```python
@dataclass
class UserContext:
    user_id: str
    preferences: dict
    session_id: str

@tool
def get_user_preferences(runtime: ToolRuntime[UserContext]) -> dict:
    """Get user preferences from context."""
    return runtime.context.preferences
```

### 3. 结构化输出

智能体可以返回结构化的响应：

```python
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    summary: str
    confidence: float
    recommendations: list[str]

agent = create_agent(
    model=model,
    tools=[],
    response_format=AnalysisResult
)
```

### 4. 对话记忆

智能体可以记住对话历史：

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[],
    checkpointer=checkpointer
)

# 使用 thread_id 维护对话状态
config = {"configurable": {"thread_id": "conversation_1"}}
response = agent.invoke({
    "messages": [{"role": "user", "content": "Hello!"}],
    "config": config
})
```

## 智能体执行

### 调用智能体

```python
# 基础调用
response = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in Tokyo?"}]
})

# 带配置的调用
config = {"configurable": {"thread_id": "1"}}
response = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather?"}],
    "config": config,
    "context": Context(user_id="1")
})
```

### 流式响应

```python
for chunk in agent.stream({
    "messages": [{"role": "user", "content": "Tell me a story"}]
}):
    print(chunk)
```

## 智能体类型

### 1. 工具调用智能体

使用函数调用与外部工具交互的智能体。

### 2. 推理智能体

能够进行复杂推理和问题解决的智能体。

### 3. 多模态智能体

能够处理文本、图像、音频等多种输入类型的智能体。

## 最佳实践

### 1. 工具设计
- 工具应该有清晰的文档字符串
- 工具应该处理错误情况
- 工具应该返回结构化的信息

### 2. 提示工程
- 提供清晰的系统提示
- 明确智能体的角色和能力
- 包含使用工具的指导

### 3. 错误处理
- 实现适当的错误处理机制
- 提供有意义的错误消息
- 考虑降级策略

### 4. 性能优化
- 使用适当的模型配置
- 实现缓存机制
- 监控智能体性能
---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/agents