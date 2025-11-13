# LangChain 模型指南

## 模型概述

LLM 是强大的人工智能工具，可以像人类一样解释和生成文本。它们足够通用，可以编写内容、翻译语言、总结和回答问题，而无需为每个任务进行专门训练。

除了文本生成，许多模型还支持：
- **工具调用** - 调用外部工具（如数据库查询或 API 调用）并在响应中使用结果
- **结构化输出** - 模型的响应被约束为遵循定义的格式
- **多模态** - 处理和返回文本以外的数据，如图像、音频和视频
- **推理** - 模型执行多步推理以得出结论

模型是智能体的推理引擎。它们驱动智能体的决策过程，确定调用哪些工具、如何解释结果以及何时提供最终答案。您选择的模型的质量和能力直接影响智能体的可靠性和性能。

## 基本用法

模型可以通过两种方式使用：

### 1. 与智能体一起使用
- 模型可以在创建智能体时动态指定

### 2. 独立使用
- 模型可以直接调用（在智能体循环之外）用于文本生成、分类或提取等任务，无需智能体框架

相同的模型接口在两种上下文中都有效，这使您可以灵活地从简单开始，并根据需要扩展到更复杂的基于智能体的工作流。

## 初始化模型

在 LangChain 中开始使用独立模型的最简单方法是使用 `init_chat_model` 从您选择的聊天模型提供商初始化一个模型：

```python
import os
from langchain.chat_models import init_chat_model

os.environ["OPENAI_API_KEY"] = "sk-..."

model = init_chat_model("gpt-4o")

response = model.invoke("Why do parrots talk?")
print(response)
```

## 关键方法

### Invoke
模型接收消息作为输入，并在生成完整响应后输出消息。

**单条消息**
```python
response = model.invoke("Why do parrots have colorful feathers?")
print(response)
```

**消息列表**
```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

conversation = [
    SystemMessage("You are a helpful assistant that translates English to French."),
    HumanMessage("Translate: I love programming."),
    AIMessage("J'adore la programmation."),
    HumanMessage("Translate: I love building applications.")
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore créer des applications.")
```

### Stream
调用模型，但在实时生成时流式传输输出。

```python
for chunk in model.stream("Why do parrots have colorful feathers?"):
    print(chunk.text, end="", flush=True)
```

### Batch
将多个请求批量发送到模型以进行更高效的处理。

```python
responses = model.batch([
    "Why do parrots have colorful feathers?",
    "How do airplanes fly?", 
    "What is quantum computing?"
])

for response in responses:
    print(response)
```

## 参数

聊天模型接受可用于配置其行为的参数。支持的完整参数集因模型和提供商而异，但标准参数包括：

- **model** (string, required) - 您想要与提供商一起使用的特定模型的名称或标识符
- **api_key** (string) - 验证模型提供商所需的密钥
- **temperature** (number) - 控制模型输出的随机性
- **timeout** (number) - 在取消请求之前等待模型响应的最长时间（秒）
- **max_tokens** (number) - 限制响应中的总令牌数
- **max_retries** (number) - 系统将重新发送请求的最大尝试次数

## 工具调用

模型可以请求调用执行任务的工具，例如从数据库获取数据、搜索网络或运行代码。

```python
# 将（可能多个）工具绑定到模型
model_with_tools = model.bind_tools([tool1, tool2])

# 工具执行循环
response = model_with_tools.invoke("What's the weather in SF?")

while response.tool_calls:
    tool_call = response.tool_calls[0]
    result = tool_call["name"](**tool_call["args"])
    response = model_with_tools.invoke([
        {"role": "user", "content": "What's the weather in SF?"},
        {"role": "assistant", "content": response},
        {"role": "tool", "content": result, "tool_call_id": tool_call["id"]}
    ])
```

## 结构化输出

结构化输出允许您将模型的响应约束为遵循定义的格式。

```python
from pydantic import BaseModel, Field

class Actor(BaseModel):
    name: str
    role: str

class MovieDetails(BaseModel):
    title: str
    year: int
    cast: list[Actor]
    genres: list[str]
    budget: float | None = Field(None, description="Budget in millions USD")

model_with_structure = model.with_structured_output(MovieDetails)
result = model_with_structure.invoke("Tell me about the movie Inception")
```

## 高级主题

### 多模态
某些模型可以处理和生成文本以外的数据，如图像、音频和视频。

### 本地模型
您可以使用 `init_chat_model` 通过指定适当的 `base_url` 参数来使用本地模型：

```python
model = init_chat_model(
    model="MODEL_NAME",
    model_provider="openai", 
    base_url="BASE_URL",
    api_key="YOUR_API_KEY",
)
```

### 提示缓存
某些提供商支持提示缓存以减少延迟和成本。

### 服务器端工具使用
某些提供商支持服务器端工具调用循环：模型可以在单个对话轮次中与网络搜索、代码解释器和其他工具交互并分析结果。

### 速率限制
管理 API 使用以避免超出配额。

## 配置模型

您可以在调用时传递配置来控制模型行为：

```python
response = model.invoke(
    "Tell me a joke",
    config={
        "run_name": "joke_generation",  # 此运行的自定义名称
        "tags": ["humor", "demo"],      # 用于分类的标签
        "metadata": {"user_id": "123"}, # 自定义元数据
        "callbacks": my_callback_handler, # 回调处理程序
    }
)
```

这些配置值在以下情况下特别有用：
- 使用 LangSmith 跟踪进行调试
- 实现自定义日志记录或监控
- 在生产中控制资源使用
- 跨复杂管道跟踪调用

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/models