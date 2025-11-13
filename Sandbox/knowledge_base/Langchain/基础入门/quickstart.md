# LangChain 快速开始

本快速入门将带您从简单设置到在几分钟内构建一个功能完整的 AI 智能体。

## 构建基础智能体

从创建一个简单的智能体开始，它可以回答问题并调用工具。该智能体将使用 Claude Sonnet 4.5 作为其语言模型，一个基本的天气函数作为工具，以及一个简单的提示来指导其行为。

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

# 运行智能体
agent.invoke({
    "messages": [{"role": "user", "content": "what is the weather in sf"}]
})
```

## 构建真实世界智能体

接下来，构建一个实用的天气预报智能体，演示关键的生产概念：
- 详细的系统提示以获得更好的智能体行为
- 与外部数据集成创建工具
- 模型配置以获得一致的响应
- 结构化输出以获得可预测的结果
- 对话记忆以实现类似聊天的交互

### 完整示例代码

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver

# 定义系统提示
SYSTEM_PROMPT = """
You are an expert weather forecaster, who speaks in puns. You have access to two tools:
- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location.
"""

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
    # A punny response (always required)
    punny_response: str
    # Any interesting information about the weather if available
    weather_conditions: str | None = None

# 设置记忆
checkpointer = InMemorySaver()

# 创建智能体
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ResponseFormat,
    checkpointer=checkpointer
)

# 运行智能体
# thread_id 是给定对话的唯一标识符
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke({
    "messages": [{"role": "user", "content": "what is the weather outside?"}],
    "config": config,
    "context": Context(user_id="1")
})

print(response['structured_response'])
# ResponseFormat(
#   punny_response="Florida is still having a 'sun-derful' day! The sunshine is playing 'ray-dio' hits all day long! I'd say it's the perfect weather for some 'solar-bration'! If you were hoping for rain, I'm afraid that idea is all 'washed up' - the forecast remains 'clear-ly' brilliant!",
#   weather_conditions="It's always sunny in Florida!"
# )

# 注意：我们可以使用相同的 thread_id 继续对话
response = agent.invoke({
    "messages": [{"role": "user", "content": "thank you!"}],
    "config": config,
    "context": Context(user_id="1")
})

print(response['structured_response'])
# ResponseFormat(
#   punny_response="You're 'thund-erfully' welcome! It's always a 'breeze' to help you stay 'current' with the weather. I'm just 'cloud'-ing around waiting to 'shower' you with more forecasts whenever you need them. Have a 'sun-sational' day in the Florida sunshine!",
#   weather_conditions=None
# )
```

## 恭喜！

您现在拥有一个可以：
- 理解上下文并记住对话
- 智能使用多个工具
- 以一致的格式提供结构化响应
- 通过上下文处理用户特定信息
- 在交互中维护对话状态

的 AI 智能体。# LangChain 快速开始

本快速入门将带您从简单设置到在几分钟内构建一个功能完整的 AI 智能体。

## 构建基础智能体

从创建一个简单的智能体开始，它可以回答问题并调用工具。该智能体将使用 Claude Sonnet 4.5 作为其语言模型，一个基本的天气函数作为工具，以及一个简单的提示来指导其行为。

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

# 运行智能体
agent.invoke({
    "messages": [{"role": "user", "content": "what is the weather in sf"}]
})
```

## 构建真实世界智能体

接下来，构建一个实用的天气预报智能体，演示关键的生产概念：
- 详细的系统提示以获得更好的智能体行为
- 与外部数据集成创建工具
- 模型配置以获得一致的响应
- 结构化输出以获得可预测的结果
- 对话记忆以实现类似聊天的交互

### 完整示例代码

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver

# 定义系统提示
SYSTEM_PROMPT = """
You are an expert weather forecaster, who speaks in puns. You have access to two tools:
- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location.
"""

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
    # A punny response (always required)
    punny_response: str
    # Any interesting information about the weather if available
    weather_conditions: str | None = None

# 设置记忆
checkpointer = InMemorySaver()

# 创建智能体
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ResponseFormat,
    checkpointer=checkpointer
)

# 运行智能体
# thread_id 是给定对话的唯一标识符
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke({
    "messages": [{"role": "user", "content": "what is the weather outside?"}],
    "config": config,
    "context": Context(user_id="1")
})

print(response['structured_response'])
# ResponseFormat(
#   punny_response="Florida is still having a 'sun-derful' day! The sunshine is playing 'ray-dio' hits all day long! I'd say it's the perfect weather for some 'solar-bration'! If you were hoping for rain, I'm afraid that idea is all 'washed up' - the forecast remains 'clear-ly' brilliant!",
#   weather_conditions="It's always sunny in Florida!"
# )

# 注意：我们可以使用相同的 thread_id 继续对话
response = agent.invoke({
    "messages": [{"role": "user", "content": "thank you!"}],
    "config": config,
    "context": Context(user_id="1")
})

print(response['structured_response'])
# ResponseFormat(
#   punny_response="You're 'thund-erfully' welcome! It's always a 'breeze' to help you stay 'current' with the weather. I'm just 'cloud'-ing around waiting to 'shower' you with more forecasts whenever you need them. Have a 'sun-sational' day in the Florida sunshine!",
#   weather_conditions=None
# )
```

## 恭喜！

您现在拥有一个可以：
- 理解上下文并记住对话
- 智能使用多个工具
- 以一致的格式提供结构化响应
- 通过上下文处理用户特定信息
- 在交互中维护对话状态

的 AI 智能体。

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/quickstart