# LangChain RAG 检索增强生成指南

## 概述

LLM 最强大的应用之一是复杂的问答（QA）聊天机器人。这些应用程序可以回答关于特定源信息的问题。这些应用程序使用一种称为检索增强生成（RAG）的技术。

本教程将展示如何基于非结构化文本数据源构建一个简单的 QA 应用程序。我们将演示：
- **RAG 智能体**：使用简单工具执行搜索。这是一个很好的通用实现。
- **两步 RAG 链**：每个查询仅使用一次 LLM 调用。这是简单查询的快速有效方法。

## 概念

我们将涵盖以下概念：
- **索引**：从源摄取数据并为其建立索引的管道。这通常在一个单独的过程中发生。
- **检索和生成**：实际的 RAG 过程，在运行时获取用户查询并从索引中检索相关数据，然后将其传递给模型。

## 组件

我们将需要从 LangChain 的集成套件中选择三个组件：

```python
import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chat_models import init_chat_model

# 设置环境变量
os.environ["OPENAI_API_KEY"] = "your-api-key"

# 初始化组件
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings)
model = init_chat_model("gpt-4")
```

## 1. 索引

本节是语义搜索教程内容的缩写版本。如果您的数据已经索引并可供搜索，或者您熟悉文档加载器、嵌入和向量存储，请跳到下一节关于检索和生成的部分。

索引通常按以下方式工作：
- **加载**：首先我们需要加载数据。这是通过文档加载器完成的。
- **分割**：文本分割器将大文档分解为较小的块。这对于索引数据和将其传递到模型都很有用，因为大块更难搜索，并且不适合模型的有限上下文窗口。
- **存储**：我们需要某个地方来存储和索引我们的分割，以便以后可以搜索它们。这通常使用向量存储和嵌入模型完成。

### 加载文档

我们需要首先加载博客文章内容。我们可以使用文档加载器，这些是对象，从源加载数据并返回文档对象列表。

```python
import bs4
from langchain_community.document_loaders import WebBaseLoader

# 仅从完整 HTML 中保留帖子标题、标题和内容
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()
print(f"Total characters: {len(docs[0].page_content)}")  # 43131
```

### 分割文档

我们加载的文档超过 42k 字符，这对于许多模型的上下文窗口来说太长了。即使对于那些可以将完整帖子放入其上下文窗口的模型，模型也很难在非常长的输入中找到信息。

为了处理这个问题，我们将文档分割为块以进行嵌入和向量存储。这应该有助于我们在运行时仅检索博客文章的最相关部分。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)
print(f"Split blog post into {len(all_splits)} sub-documents.")  # 66
```

### 存储文档

现在我们需要索引我们的 66 个文本块，以便我们可以在运行时搜索它们。

```python
document_ids = vector_store.add_documents(documents=all_splits)
```

这完成了管道的索引部分。此时我们有一个可查询的向量存储，包含我们博客文章的块内容。给定用户问题，我们应该能够返回回答问题的博客文章片段。

## 2. 检索和生成

RAG 应用程序通常按以下方式工作：
- **检索**：给定用户输入，使用检索器从存储中检索相关分割。
- **生成**：模型使用包含问题和检索数据的提示产生答案。

### RAG 智能体

RAG 应用程序的一种表述是作为一个简单的智能体，具有检索信息的工具。

```python
from langchain.tools import tool

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

from langchain.agents import create_agent

tools = [retrieve_context]

# 如果需要，指定自定义指令
prompt = (
    "You have access to a tool that retrieves context from a blog post. "
    "Use the tool to help answer user queries."
)

agent = create_agent(model, tools, system_prompt=prompt)
```

让我们测试一下：

```python
query = (
    "What is the standard method for Task Decomposition?\n\n"
    "Once you get the answer, look up common extensions of that method."
)

for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()
```

### RAG 链

在智能体 RAG 表述中，我们允许 LLM 自行决定生成工具调用来帮助回答用户查询。

**优点**：
- 两次推理调用 - 当执行搜索时，需要一次调用来生成查询，另一次来产生最终响应。
- 上下文搜索查询 - 通过将搜索视为具有查询输入的工具，LLM 制作自己的查询，这些查询包含对话上下文。
- 允许多次搜索 - LLM 可以执行多次搜索以支持单个用户查询。

**缺点**：
- 减少控制 - LLM 可能在需要时跳过搜索，或在不需要时发出额外搜索。

另一种常见方法是两步链，其中我们总是运行搜索（可能使用原始用户查询）并将结果作为单个 LLM 查询的上下文。这导致每个查询只有一次推理调用，以灵活性为代价换取减少的延迟。

```python
from langchain.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    """Inject context into state messages."""
    last_query = request.text
    retrieved_docs = vector_store.similarity_search(last_query)
    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    system_message = (
        "You are a helpful assistant. "
        "Answer the user's question based on the following context:\n\n"
        f"{docs_content}"
    )
    return system_message

from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=[],  # 无工具
    middleware=[prompt_with_context]
)

# 测试
query = "What is task decomposition?"
for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()
```

## 总结

- **RAG 智能体**：灵活，允许多次搜索，但需要更多 LLM 调用
- **两步 RAG 链**：快速，每个查询一次 LLM 调用，但灵活性较低

选择哪种方法取决于您的具体需求：对于复杂查询和需要多次搜索的场景，使用智能体；对于简单查询和性能关键场景，使用两步链。

---

**原始文档URL**: https://docs.langchain.com/oss/python/langchain/rag
**整理时间**: 2025-11-10