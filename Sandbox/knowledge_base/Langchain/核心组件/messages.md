# LangChain 消息指南

## 消息概述

消息是 LangChain 中模型上下文的基本单位。它们表示模型的输入和输出，携带表示与 LLM 交互时对话状态所需的内容和元数据。

消息是包含以下内容的对象：
- **角色** - 标识消息类型（例如系统、用户）
- **内容** - 表示消息的实际内容（如文本、图像、音频、文档等）

## 基本用法

使用消息的最简单方法是创建消息对象并在调用时将它们传递给模型。

```python
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage

model = init_chat_model("gpt-5-nano")

system_msg = SystemMessage("You are a helpful assistant.")
human_msg = HumanMessage("Hello, how are you?")

# 与聊天模型一起使用
messages = [system_msg, human_msg]
response = model.invoke(messages)  # 返回 AIMessage
```

## 文本提示

文本提示是字符串 - 适用于不需要保留对话历史的简单生成任务。

```python
response = model.invoke("Write a haiku about spring")
```

使用文本提示的情况：
- 您有单个独立的请求
- 不需要对话历史
- 想要最少的代码复杂性

## 消息提示

或者，您可以通过提供消息对象列表将消息列表传递给模型。

**消息对象格式**
```python
from langchain.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage("You are a poetry expert"),
    HumanMessage("Write a haiku about spring"),
    AIMessage("Cherry blossoms bloom...")  # 来自之前的响应
]
```

**字典格式**
```python
messages = [
    {"role": "system", "content": "You are a poetry expert"},
    {"role": "user", "content": "Write a haiku about spring"},
    {"role": "assistant", "content": "Cherry blossoms bloom..."}
]
```

## 消息类型

### 系统消息

系统消息设置模型的上下文和行为。您可以使用系统消息来设置语气、定义模型的角色并为响应建立指导原则。

**基本指令**
```python
system_msg = SystemMessage("You are a helpful coding assistant.")
messages = [system_msg, HumanMessage("How do I create a REST API?")]
response = model.invoke(messages)
```

**详细角色**
```python
from langchain.messages import SystemMessage, HumanMessage

system_msg = SystemMessage("""
You are a senior Python developer with expertise in web frameworks.
Be concise but thorough in your explanations.
""")

messages = [system_msg, HumanMessage("How do I create a REST API?")]
response = model.invoke(messages)
```

### 人类消息

HumanMessage 表示用户输入和交互。它们可以包含文本、图像、音频、文件和任何其他数量的多模态内容。

**文本内容**
```python
# 消息对象
response = model.invoke(HumanMessage("What is machine learning?"))

# 字符串快捷方式
response = model.invoke("What is machine learning?")
```

**消息元数据**
```python
human_msg = HumanMessage(
    content="Hello.",
    metadata={"user_id": "123", "timestamp": "2024-01-01"}
)
```

### AI 消息

AIMessage 表示模型调用的输出。它们可以包括多模态数据、工具调用和您稍后可以访问的提供商特定元数据。

```python
response = model.invoke("Explain AI")
print(type(response))  # <class 'langchain_core.messages.AIMessage'>
```

**手动创建 AI 消息**
```python
from langchain.messages import AIMessage, SystemMessage, HumanMessage

# 手动创建 AI 消息（例如，用于对话历史）
ai_msg = AIMessage("I'd be happy to help you with that question.")

# 添加到对话历史
messages = [
    SystemMessage("You are a helpful assistant"),
    HumanMessage("Can you help me?"),
    ai_msg,  # 插入，就像来自模型一样
    HumanMessage("Great.")
]

response = model.invoke(messages)
```

**属性**
- `text` (string) - 消息的文本内容
- `content` (string | dict) - 消息的原始内容
- `content_blocks` (ContentBlock) - 消息的标准化内容块
- `tool_calls` (dict | None) - 模型进行的工具调用
- `response_metadata` (ResponseMetadata | None) - 消息的响应元数据

### 工具调用

当模型进行工具调用时，它们包含在 AIMessage 中：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5-nano")

def get_weather(location: str) -> str:
    """Get the weather at a location."""
    return f"It's sunny in {location}!"

model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("What's the weather in Paris?")

for tool_call in response.tool_calls:
    print(f"Tool: {tool_call['name']}")
    print(f"Args: {tool_call['args']}")
    print(f"ID: {tool_call['id']}")
```

### 令牌使用

AIMessage 可以在其 `usage_metadata` 字段中保存令牌计数和其他使用元数据：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5-nano")
response = model.invoke("Hello")

print(response.usage_metadata)
```

### 流式传输和块

在流式传输期间，您将收到可以组合成完整消息对象的 AIMessageChunk 对象：

```python
chunks = []
full_message = None

for chunk in model.stream("Hi"):
    chunks.append(chunk)
    print(chunk.text, end="", flush=True)
    full_message = chunk if full_message is None else full_message + chunk

print(f"\nFull message: {full_message.text}")
```

## 工具消息

ToolMessage 用于将单个工具执行的结果传递回模型。工具可以直接生成 ToolMessage 对象。

```python
from langchain.messages import ToolMessage

# 发送到模型
message_content = "It was the best of times, it was the worst of times..."

# 工件可用于下游处理
artifact = {"document_id": "doc_123", "page": 0}

tool_message = ToolMessage(
    content=message_content,
    tool_call_id="call_123",
    name="search_books",
    artifact=artifact,
)
```

**属性**
- `content` (string, required) - 工具调用的字符串化输出
- `tool_call_id` (string, required) - 此消息响应的工具调用的 ID
- `name` (string, required) - 被调用的工具的名称
- `artifact` (dict) - 不发送到模型但可以以编程方式访问的附加数据

## 消息内容

您可以将消息的内容视为发送到模型的数据负载。消息有一个松散类型化的 `content` 属性，支持字符串和无类型对象的列表。

```python
from langchain.messages import HumanMessage

# 字符串内容
human_message = HumanMessage("Hello, how are you?")

# 提供商原生格式（例如，OpenAI）
human_message = HumanMessage(content=[
    {"type": "text", "text": "Hello, how are you?"},
    {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
])

# 标准内容块列表
human_message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Hello, how are you?"},
    {"type": "image", "url": "https://example.com/image.jpg"}
])
```

## 标准内容块

LangChain 为消息内容提供了跨提供商工作的标准表示。消息对象实现了一个 `content_blocks` 属性，该属性将惰性解析 `content` 属性为标准化的、类型安全的表示。

```python
from langchain.messages import AIMessage

message = AIMessage(
    content=[
        {"type": "thinking", "thinking": "..."},
        {"type": "text", "text": "..."}
    ],
    response_metadata={"model_provider": "anthropic"}
)

message.content_blocks
```

## 多模态

LangChain 包含可用于跨提供商的这些数据的标准类型。聊天模型可以接受多模态数据作为输入并生成它作为输出。

**图像输入**
```python
# 来自 URL
message = [
    {"role": "user", "content": [
        {"type": "text", "text": "Describe the content of this image."},
        {"type": "image", "url": "https://example.com/image.jpg"}
    ]}
]

# 来自 base64 数据
message = [
    {"role": "user", "content": [
        {"type": "text", "text": "Describe the content of this image."},
        {"type": "image", "base64": "AAAAIGZ0eXBtcDQy...", "mime_type": "image/jpeg"}
    ]}
]
```

**PDF 文档输入**
```python
message = [
    {"role": "user", "content": [
        {"type": "text", "text": "Summarize this document."},
        {"type": "file", "url": "https://example.com/document.pdf"}
    ]}
]
```

并非所有模型都支持所有文件类型。请检查模型提供商的参考以了解支持的格式和大小限制。

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/messages