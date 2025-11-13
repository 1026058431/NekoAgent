# LangChain 上下文工程指南

## 概述

构建智能体（或任何 LLM 应用程序）的困难部分是使它们足够可靠。虽然它们可能适用于原型，但在实际用例中经常失败。

当智能体失败时，通常是因为智能体内部的 LLM 调用采取了错误的行动或没有按照我们的预期执行。

**上下文工程**是提供正确的信息和工具，以正确的格式，使 LLM 能够完成任务。这是 AI 工程师的首要工作。

缺乏正确的上下文是更可靠智能体的首要障碍，LangChain 的智能体抽象是专门设计来促进上下文工程的。

**新手上路**：从概念概述开始，了解不同类型的上下文以及何时使用它们。

## 为什么智能体会失败

LLM 失败的原因有两个：
1. 底层 LLM 不够强大
2. 没有将正确的上下文传递给 LLM

更常见的是 - 实际上是第二个原因导致智能体不可靠。

## 智能体循环

典型的智能体循环包括两个主要步骤：
1. **模型调用** - 使用提示和可用工具调用 LLM，返回响应或执行工具的请求
2. **工具执行** - 执行 LLM 请求的工具，返回工具结果

此循环持续进行，直到 LLM 决定完成。

## 您可以控制的内容

要构建可靠的智能体，您需要控制智能体循环的每个步骤中发生的事情，以及步骤之间发生的事情。

| 上下文类型 | 您控制的内容 | 瞬态或持久 |
|------------|--------------|------------|
| **模型上下文** | 进入模型调用的内容（指令、消息历史、工具、响应格式） | 瞬态 |
| **工具上下文** | 工具可以访问和产生的内容（对状态、存储、运行时上下文的读写） | 持久 |
| **生命周期上下文** | 模型和工具调用之间发生的事情（总结、护栏、日志记录等） | 持久 |

**瞬态上下文**：LLM 在单次调用中看到的内容。您可以修改消息、工具或提示，而不改变保存在状态中的内容。

**持久上下文**：在轮次之间保存在状态中的内容。生命周期钩子和工具写入永久修改此内容。

## 数据源

在此过程中，您的智能体访问（读取/写入）不同的数据源：

| 数据源 | 也称为 | 范围 | 示例 |
|--------|--------|------|------|
| **Runtime Context** | 静态配置 | 对话范围 | 用户 ID、API 密钥、数据库连接、权限、环境设置 |
| **State** | 短期记忆 | 对话范围 | 当前消息、上传的文件、身份验证状态、工具结果 |
| **Store** | 长期记忆 | 跨对话 | 用户偏好、提取的见解、记忆、历史数据 |

## 工作原理

LangChain 中间件是使上下文工程对使用 LangChain 的开发人员实用的底层机制。

中间件允许您钩入智能体生命周期的任何步骤并：
- 更新上下文
- 跳转到智能体生命周期中的不同步骤

在本指南中，您将经常看到中间件 API 作为上下文工程手段的使用。

## 模型上下文

控制进入每个模型调用的内容 - 指令、可用工具、使用哪个模型以及输出格式。这些决策直接影响可靠性和成本。

### 系统提示

系统提示设置 LLM 的行为和能力。不同的用户、上下文或对话阶段需要不同的指令。

成功的智能体利用记忆、偏好和配置来为对话的当前状态提供正确的指令。

**从状态访问消息计数或对话上下文**：
```python
from langchain.agents import create_agent
from langchain.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    # request.messages 是 request.state["messages"] 的快捷方式
    message_count = len(request.messages)
    base = "You are a helpful assistant. "
    
    if message_count > 10:
        base += "\nThis is a long conversation - be extra concise. "
    
    return base

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[state_aware_prompt]
)
```

### 消息

消息构成发送给 LLM 的提示。管理消息的内容至关重要，以确保 LLM 有正确的信息来良好响应。

**从状态注入上传的文件上下文**：
```python
from langchain.agents import create_agent
from langchain.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable

@wrap_model_call
def inject_file_context(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Inject context about files user has uploaded this session."""
    
    # 从状态读取：获取上传文件的元数据
    uploaded_files = request.state.get("uploaded_files", [])
    
    if uploaded_files:
        # 构建关于可用文件的上下文
        file_descriptions = []
        for file in uploaded_files:
            file_descriptions.append(
                f"- {file['name']} ({file['type']}): {file['summary']}"
            )
        
        file_context = f"""Files you have access to in this conversation:
{chr(10).join(file_descriptions)}

Reference these files when answering questions."""
        
        # 在最近消息之前注入文件上下文
        messages = [
            *request.messages[:-1],
            {"role": "user", "content": file_context},
            request.messages[-1]
        ]
        
        request = request.override(messages=messages)
    
    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[inject_file_context]
)
```

**瞬态与持久消息更新**：
上面的示例使用 `wrap_model_call` 进行瞬态更新 - 修改发送给模型的消息以进行单次调用，而不改变保存在状态中的内容。

### 工具

工具让模型与数据库、API 和外部系统交互。您如何定义和选择工具直接影响模型是否能够有效完成任务。

#### 定义工具

每个工具都需要清晰的名称、描述、参数名称和参数描述。这些不仅仅是元数据 - 它们指导模型关于何时以及如何使用工具的推理。

```python
from langchain.tools import tool

@tool(parse_docstring=True)
def search_orders(
    user_id: str,
    status: str,
    limit: int = 10
) -> str:
    """Search for user orders by status.
    
    Use this when the user asks about order history or wants to check order status.
    Always filter by the provided status.
    
    Args:
        user_id: Unique identifier for the user
        status: Order status: 'pending', 'shipped', or 'delivered'
        limit: Maximum number of results to return
    """
    # 实现在这里
    pass
```

#### 选择工具

并非每个工具都适用于每种情况。工具过多可能会使模型不堪重负（过载上下文）并增加错误；工具过少会限制能力。

动态工具选择基于身份验证状态、用户权限、功能标志或对话阶段调整可用工具集。

**在达到某些对话里程碑后启用高级工具**：
```python
from langchain.agents import create_agent
from langchain.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable

@wrap_model_call
def state_based_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Filter tools based on conversation State."""
    
    # 从状态读取：检查用户是否已通过身份验证
    state = request.state
    is_authenticated = state.get("authenticated", False)
    message_count = len(state["messages"])
    
    # 仅在身份验证后启用敏感工具
    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith("public_")]
        request = request.override(tools=tools)
    elif message_count < 5:
        # 在对话早期限制工具
        tools = [t for t in request.tools if t.name != "advanced_search"]
        request = request.override(tools=tools)
    
    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[public_search, private_search, advanced_search],
    middleware=[state_based_tools]
)
```

### 模型

不同的模型有不同的优势、成本和上下文窗口。为手头的任务选择合适的模型，这可能在智能体运行期间发生变化。

**基于状态中的对话长度使用不同的模型**：
```python
from langchain.agents import create_agent
from langchain.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from typing import Callable

@wrap_model_call
def state_based_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Select model based on conversation length from State."""
    
    # request.messages 是 request.state["messages"] 的快捷方式
    message_count = len(request.messages)
    
    if message_count > 20:
        # 长对话 - 使用更便宜的模型
        model = init_chat_model("gpt-4o-mini")
        request = request.override(model=model)
    
    return handler(request)

agent = create_agent(
    model="gpt-4o-mini",
    tools=[...],
    middleware=[state_based_model]
)
```

### 响应格式

结构化输出将非结构化文本转换为经过验证的结构化数据。当提取特定字段或为下游系统返回数据时，自由格式文本是不够的。

**工作原理**：当您提供模式作为响应格式时，模型的最终响应保证符合该模式。智能体运行模型 + 工具调用循环，直到模型完成调用工具，然后将最终响应强制转换为提供的格式。

#### 定义格式

模式定义指导模型。字段名称、类型和描述确切指定输出应遵循的格式。

```python
from pydantic import BaseModel, Field

class CustomerSupportTicket(BaseModel):
    """Structured ticket information extracted from customer message."""
    issue_type: str = Field(description="Type of issue reported")
    priority: str = Field(description="Urgency level: 'low', 'medium', 'high'")
    summary: str = Field(description="Brief description of the issue")
```

#### 选择格式

**基于对话状态配置结构化输出**：
```python
from langchain.agents import create_agent
from langchain.middleware import wrap_model_call, ModelRequest, ModelResponse
from pydantic import BaseModel, Field
from typing import Callable

class SimpleResponse(BaseModel):
    """Simple response for early conversation."""
    answer: str = Field(description="A brief answer")

class DetailedResponse(BaseModel):
    """Detailed response for established conversation."""
    answer: str = Field(description="A comprehensive answer")
    reasoning: str = Field(description="Step-by-step reasoning")
    sources: list[str] = Field(description="Sources referenced")

@wrap_model_call
def state_based_output(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Configure response format based on conversation state."""
    
    # request.messages 是 request.state["messages"] 的快捷方式
    message_count = len(request.messages)
    
    if message_count < 3:
        # 早期对话 - 使用简单格式
        request = request.override(response_format=SimpleResponse)
    else:
        # 已建立的对话 - 使用详细格式
        request = request.override(response_format=DetailedResponse)
    
    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[state_based_output]
)
```

## 工具上下文

工具的特殊之处在于它们既读取又写入上下文。在最基本的情况下，当工具执行时，它接收 LLM 的请求参数并返回工具消息。

工具完成其工作并产生结果。

### 读取

大多数真实世界的工具需要的不仅仅是 LLM 的参数。工具从状态、存储和运行时上下文读取以访问此信息。

**从状态读取以检查当前会话信息**：
```python
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent

@tool
def check_authentication(
    runtime: ToolRuntime
) -> str:
    """Check if user is authenticated."""
    
    # 从状态读取：检查当前身份验证状态
    current_state = runtime.state
    is_authenticated = current_state.get("authenticated", False)
    
    if is_authenticated:
        return "User is authenticated"
    else:
        return "User is not authenticated"
```

### 写入

工具可以更新状态、存储或运行时上下文以跟踪会话特定的信息。

**写入状态以跟踪会话特定信息**：
```python
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langgraph.types import Command

@tool
def authenticate_user(
    password: str,
    runtime: ToolRuntime
) -> Command:
    """Authenticate user and update State."""
    
    # 执行身份验证（简化）
    if password == "correct":
        # 写入状态：使用 Command 标记为已通过身份验证
        return Command(
            update={"authenticated": True},
        )
    else:
        return Command(update={"authenticated": False})

agent = create_agent(
    model="gpt-4o",
    tools=[authenticate_user]
)
```

## 生命周期上下文

控制核心智能体步骤之间发生的事情 - 拦截数据流以实现横切关注点，如总结、护栏和日志记录。

正如您在模型上下文和工具上下文中看到的，中间件是使上下文工程实用的机制。

### 示例：总结

最常见的生命周期模式之一是当对话历史过长时自动压缩对话历史。

与模型上下文中显示的瞬态消息修剪不同，总结持久更新状态 - 永久用总结替换旧消息，该总结保存用于所有未来轮次。

LangChain 为此提供内置中间件：
```python
from langchain.agents import create_agent
from langchain.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[SummarizationMiddleware()]
)
```

对于持久更新修改状态（如生命周期上下文中的总结示例），使用生命周期钩子如 `before_model` 或 `after_model` 永久更新对话历史。

## 最佳实践

1. **从简单开始**：首先使用基本上下文，然后根据需要添加复杂性
2. **使用中间件进行横切关注点**：总结、护栏、日志记录等
3. **平衡工具数量**：工具过多会混淆模型，工具过少会限制能力
4. **基于状态动态调整**：根据对话阶段、用户权限等调整上下文
5. **测试不同场景**：确保您的上下文工程在各种用例中都能正常工作

## 相关资源

- 中间件文档 - 有关内置中间件、可用钩子以及如何创建自定义中间件的完整详细信息
- 工具文档 - 在工具中访问状态、存储和运行时上下文的全面示例
- 动态选择工具 - 更多示例

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/context-engineering