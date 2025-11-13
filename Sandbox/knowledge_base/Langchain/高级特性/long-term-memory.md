# 长期记忆

LangChain智能体使用LangGraph持久化来启用长期记忆。这是一个更高级的主题，需要了解LangGraph才能使用。

## 概述

LangChain智能体使用LangGraph持久化来启用长期记忆。这是一个更高级的主题，需要了解LangGraph才能使用。

## 内存存储

LangGraph将长期记忆作为JSON文档存储在存储中。每个内存都在自定义命名空间（类似于文件夹）和不同键（如文件名）下组织。命名空间通常包括用户或组织ID或其他标签，以便更容易组织信息。

这种结构支持内存的分层组织。然后通过内容过滤器支持跨命名空间搜索。

```python
from langgraph.store.memory import InMemoryStore

def embed(texts: list[str]) -> list[list[float]]:
    # 替换为实际的嵌入函数或LangChain嵌入对象
    return [[1.0, 2.0] * len(texts)]

# InMemoryStore将数据保存到内存字典中。在生产使用中使用数据库支持的存储。
store = InMemoryStore(index={"embed": embed, "dims": 2})

user_id = "my-user"
application_context = "chitchat"
namespace = (user_id, application_context)

store.put(
    namespace,
    "a-memory",
    {
        "rules": [
            "User likes short, direct language",
            "User only speaks English & python",
        ],
        "my-key": "my-value",
    },
)

# 通过ID获取"memory"
item = store.get(namespace, "a-memory")

# 在此命名空间内搜索"memories"，过滤内容等价性，按向量相似性排序
items = store.search(
    namespace,
    filter={"my-key": "my-value"},
    query="language preferences"
)
```

有关内存存储的更多信息，请参阅[持久化指南](https://langchain-ai.github.io/langgraph/guide/persistence/)。

## 在工具中读取长期记忆

智能体可以用来查找用户信息的工具

```python
from dataclasses import dataclass
from langchain_core.runnables import RunnableConfig
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

# InMemoryStore将数据保存到内存字典中。在生产使用中使用数据库支持的存储。
store = InMemoryStore()

# 使用put方法将示例数据写入存储
store.put(
    ("users",),  # 命名空间以将相关数据分组在一起（用户命名空间用于用户数据）
    "user_123",  # 命名空间内的键（用户ID作为键）
    {
        "name": "John Smith",
        "language": "English",
    }  # 为给定用户存储的数据
)

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """Look up user info."""
    # 访问存储 - 与提供给 `create_agent` 的相同
    store = runtime.store
    user_id = runtime.context.user_id
    
    # 从存储中检索数据 - 返回带有值和元数据的StoreValue对象
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_user_info],
    # 将存储传递给智能体 - 使智能体在运行工具时能够访问存储
    store=store,
    context_schema=Context
)

# 运行智能体
agent.invoke(
    {"messages": [{"role": "user", "content": "look up user information"}]},
    context=Context(user_id="user_123")
)
```

## 从工具写入长期记忆

更新用户信息的工具示例

```python
from dataclasses import dataclass
from typing_extensions import TypedDict
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore

# InMemoryStore将数据保存到内存字典中。在生产使用中使用数据库支持的存储。
store = InMemoryStore()

@dataclass
class Context:
    user_id: str

# TypedDict为LLM定义用户信息的结构
class UserInfo(TypedDict):
    name: str

# 允许智能体更新用户信息的工具（对聊天应用程序有用）
@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Save user info."""
    # 访问存储 - 与提供给 `create_agent` 的相同
    store = runtime.store
    user_id = runtime.context.user_id
    
    # 将数据存储在存储中（命名空间，键，数据）
    store.put(("users",), user_id, user_info)
    return "Successfully saved user info."

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[save_user_info],
    store=store,
    context_schema=Context
)

# 运行智能体
agent.invoke(
    {"messages": [{"role": "user", "content": "My name is John Smith"}]},
    # user_id在上下文中传递以标识正在更新谁的信息
    context=Context(user_id="user_123")
)

# 你可以直接访问存储以获取值
store.get(("users",), "user_123").value
```
---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/long-term-memory