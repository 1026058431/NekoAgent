# LangChain 结构化输出指南

## 概述

结构化输出允许智能体以特定的、可预测的格式返回数据。您无需解析自然语言响应，而是获得结构化数据，形式为 JSON 对象、Pydantic 模型或数据类，您的应用程序可以直接使用。

LangChain 的 `create_agent` 自动处理结构化输出。用户设置他们期望的结构化输出模式，当模型生成结构化数据时，它会被捕获、验证并返回到智能体状态的 `'structured_response'` 键中。

```python
def create_agent(
    ...
    response_format: Union[
        ToolStrategy[StructuredResponseT],
        ProviderStrategy[StructuredResponseT],
        type[StructuredResponseT],
    ]
)
```

**响应格式**
控制智能体如何返回结构化数据：
- `ToolStrategy[StructuredResponseT]`：使用工具调用进行结构化输出
- `ProviderStrategy[StructuredResponseT]`：使用提供商原生结构化输出
- `type[StructuredResponseT]`：模式类型 - 基于模型能力自动选择最佳策略
- `None`：无结构化输出

当直接提供模式类型时，LangChain 自动选择：
- 对于支持原生结构化输出的模型（例如 OpenAI、Grok）使用 `ProviderStrategy`
- 对于所有其他模型使用 `ToolStrategy`

结构化响应返回到智能体最终状态的 `structured_response` 键中。

## 提供商策略

一些模型提供商通过其 API 原生支持结构化输出（目前仅 OpenAI 和 Grok）。当可用时，这是最可靠的方法。

要使用此策略，请配置 `ProviderStrategy`：

```python
class ProviderStrategy(Generic[SchemaT]):
    schema: type[SchemaT]
```

**schema** (required) - 定义结构化输出格式的模式。支持：
- Pydantic 模型：具有字段验证的 BaseModel 子类
- 数据类：具有类型注解的 Python 数据类
- TypedDict：类型化字典类
- JSON Schema：具有 JSON 模式规范的字典

当您直接将模式类型传递给 `create_agent.response_format` 并且模型支持原生结构化输出时，LangChain 自动使用 `ProviderStrategy`：

**Pydantic 模型示例**
```python
from pydantic import BaseModel
from langchain.agents import create_agent

class ContactInfo(BaseModel):
    """Contact information for a person."""
    name: str  # Field(description="The name of the person")
    email: str  # Field(description="The email address of the person")
    phone: str  # Field(description="The phone number of the person")

agent = create_agent(
    model="gpt-5",
    tools=tools,
    response_format=ContactInfo  # 自动选择 ProviderStrategy
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
})

result["structured_response"]  # ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```

提供商原生结构化输出提供高可靠性和严格验证，因为模型提供商强制执行模式。当可用时使用它。

如果提供商原生支持您选择的模型的结构化输出，在功能上等同于写 `response_format=ProductReview` 而不是 `response_format=ToolStrategy(ProductReview)`。在任何一种情况下，如果不支持结构化输出，智能体将回退到工具调用策略。

## 工具调用策略

对于不支持原生结构化输出的模型，LangChain 使用工具调用来实现相同的结果。这适用于所有支持工具调用的模型，这是大多数现代模型。

要使用此策略，请配置 `ToolStrategy`：

```python
class ToolStrategy(Generic[SchemaT]):
    schema: type[SchemaT]
    tool_message_content: str | None
    handle_errors: Union[
        bool,
        str,
        type[Exception],
        tuple[type[Exception], ...],
        Callable[[Exception], str],
    ]
```

**schema** (required) - 定义结构化输出格式的模式。支持：
- Pydantic 模型：具有字段验证的 BaseModel 子类
- 数据类：具有类型注解的 Python 数据类
- TypedDict：类型化字典类
- JSON Schema：具有 JSON 模式规范的字典
- 联合类型：多个模式选项。模型将基于上下文选择最合适的模式。

**tool_message_content** - 生成结构化输出时返回的工具消息的自定义内容。如果未提供，默认为显示结构化响应数据的消息。

**handle_errors** - 结构化输出验证失败的错误处理策略。默认为 True。

**Pydantic 模型示例**
```python
from pydantic import BaseModel, Field
from typing import Literal
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class ProductReview(BaseModel):
    """Analysis of a product review."""
    rating: int | None = Field(description="The rating of the product", ge=1, le=5)
    sentiment: Literal["positive", "negative"] = Field(description="The sentiment of the review")
    key_points: list[str] = Field(description="The key points of the review. Lowercase, 1-3 words each.")

agent = create_agent(
    model="gpt-5",
    tools=tools,
    response_format=ToolStrategy(ProductReview)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Analyze this review: 'Great product: 5 out of 5 stars. Fast shipping, but expensive'"}]
})

result["structured_response"]  # ProductReview(rating=5, sentiment='positive', key_points=['fast shipping', 'expensive'])
```

## 自定义工具消息内容

`tool_message_content` 参数允许您自定义生成结构化输出时出现在对话历史中的消息：

```python
from pydantic import BaseModel, Field
from typing import Literal
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class MeetingAction(BaseModel):
    """Action items extracted from a meeting transcript."""
    task: str = Field(description="The specific task to be completed")
    assignee: str = Field(description="Person responsible for the task")
    priority: Literal["low", "medium", "high"] = Field(description="Priority level")

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(
        schema=MeetingAction,
        tool_message_content="Action item captured and added to meeting notes!"
    )
)

agent.invoke({
    "messages": [{"role": "user", "content": "From our meeting: Sarah needs to update the project timeline as soon as possible"}]
})
```

**输出：**
```
Human Message
  From our meeting: Sarah needs to update the project timeline as soon as possible

Ai Message
  Tool Calls:
    MeetingAction (call_1)
      Call ID: call_1
      Args:
        task: Update the project timeline
        assignee: Sarah
        priority: high

Tool Message
  Name: MeetingAction
  Action item captured and added to meeting notes!
```

如果没有 `tool_message_content`，我们的最终 ToolMessage 将是：
```
Tool Message
  Name: MeetingAction
  Returning structured response: {'task': 'update the project timeline', 'assignee': 'Sarah', 'priority': 'high'}
```

## 错误处理

模型在通过工具调用生成结构化输出时可能会出错。LangChain 提供智能重试机制来自动处理这些错误。

### 多个结构化输出错误

当模型错误地调用多个结构化输出工具时，智能体在 ToolMessage 中提供错误反馈并提示模型重试：

```python
from pydantic import BaseModel, Field
from typing import Union
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class ContactInfo(BaseModel):
    name: str = Field(description="Person's name")
    email: str = Field(description="Email address")

class EventDetails(BaseModel):
    event_name: str = Field(description="Name of the event")
    date: str = Field(description="Event date")

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(Union[ContactInfo, EventDetails])  # 默认：handle_errors=True
)

agent.invoke({
    "messages": [{"role": "user", "content": "Extract info: John Doe (john@email.com) is organizing Tech Conference on March 15th"}]
})
```

**输出：**
```
Human Message
  Extract info: John Doe (john@email.com) is organizing Tech Conference on March 15th

None

Ai Message
  Tool Calls:
    ContactInfo (call_1)
      Call ID: call_1
      Args:
        name: John Doe
        email: john@email.com
    EventDetails (call_2)
      Call ID: call_2
      Args:
        event_name: Tech Conference
        date: March 15th

Tool Message
  Name: ContactInfo
  Error: Model incorrectly returned multiple structured responses (ContactInfo, EventDetails) when only one is expected. Please fix your mistakes.

Tool Message
  Name: EventDetails
  Error: Model incorrectly returned multiple structured responses (ContactInfo, EventDetails) when only one is expected. Please fix your mistakes.

Ai Message
  Tool Calls:
    ContactInfo (call_3)
      Call ID: call_3
      Args:
        name: John Doe
        email: john@email.com

Tool Message
  Name: ContactInfo
  Returning structured response: {'name': 'John Doe', 'email': 'john@email.com'}
```

### 模式验证错误

当结构化输出与预期模式不匹配时，智能体提供特定的错误反馈：

```python
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class ProductRating(BaseModel):
    rating: int | None = Field(description="Rating from 1-5", ge=1, le=5)
    comment: str = Field(description="Review comment")

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(ProductRating),  # 默认：handle_errors=True
    system_prompt="You are a helpful assistant that parses product reviews. Do not make any field or value up."
)

agent.invoke({
    "messages": [{"role": "user", "content": "Parse this: Amazing product, 10/10!"}]
})
```

**输出：**
```
Human Message
  Parse this: Amazing product, 10/10!

Ai Message
  Tool Calls:
    ProductRating (call_1)
      Call ID: call_1
      Args:
        rating: 10
        comment: Amazing product

Tool Message
  Name: ProductRating
  Error: Failed to parse structured output for tool 'ProductRating': 1 validation error for ProductRating.rating
    Input should be less than or equal to 5 [type=less_than_equal, input_value=10, input_type=int]. Please fix your mistakes.

Ai Message
  Tool Calls:
    ProductRating (call_2)
      Call ID: call_2
      Args:
        rating: 5
        comment: Amazing product

Tool Message
  Name: ProductRating
  Returning structured response: {'rating': 5, 'comment': 'Amazing product'}
```

## 错误处理策略

您可以使用 `handle_errors` 参数自定义错误处理方式：

### 自定义错误消息
```python
ToolStrategy(
    schema=ProductRating,
    handle_errors="Please provide a valid rating between 1-5 and include a comment."
)
```

如果 `handle_errors` 是字符串，智能体将始终提示模型使用固定的工具消息重试：
```
Tool Message
  Name: ProductRating
  Please provide a valid rating between 1-5 and include a comment.
```

### 仅处理特定异常
```python
ToolStrategy(
    schema=ProductRating,
    handle_errors=ValueError  # 仅在 ValueError 时重试，其他异常引发
)
```

如果 `handle_errors` 是异常类型，智能体仅在引发的异常是指定类型时才重试（使用默认错误消息）。在所有其他情况下，异常将被引发。

### 处理多个异常类型
```python
ToolStrategy(
    schema=ProductRating,
    handle_errors=(ValueError, TypeError)  # 在 ValueError 和 TypeError 时重试
)
```

如果 `handle_errors` 是异常元组，智能体仅在引发的异常是指定类型之一时才重试（使用默认错误消息）。在所有其他情况下，异常将被引发。

### 自定义错误处理程序函数
```python
def custom_error_handler(error: Exception) -> str:
    if isinstance(error, StructuredOutputValidationError):
        return "There was an issue with the format. Try again."
    elif isinstance(error, MultipleStructuredOutputsError):
        return "Multiple structured outputs were returned. Pick the most relevant one."
    else:
        return f"Error: {str(error)}"

ToolStrategy(
    schema=ToolStrategy(Union[ContactInfo, EventDetails]),
    handle_errors=custom_error_handler
)
```

在 `StructuredOutputValidationError` 时：
```
Tool Message
  Name: ToolStrategy
  There was an issue with the format. Try again.
```

在 `MultipleStructuredOutputsError` 时：
```
Tool Message
  Name: ToolStrategy
  Multiple structured outputs were returned. Pick the most relevant one.
```

在其他错误时：
```
Tool Message
  Name: ToolStrategy
  Error: error message
```

### 无错误处理
```python
response_format = ToolStrategy(
    schema=ProductRating,
    handle_errors=False  # 所有错误都引发
)
```

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/structured-output