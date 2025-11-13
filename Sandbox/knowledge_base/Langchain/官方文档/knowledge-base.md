# LangChain 知识库构建指南

## 概述

本教程将帮助您熟悉 LangChain 的文档加载器、嵌入和向量存储抽象。这些抽象旨在支持从（向量）数据库和其他来源检索数据，以便与 LLM 工作流集成。

在这里，我们将构建一个基于 PDF 文档的搜索引擎。这将允许我们检索与输入查询相似的 PDF 段落。本指南还包括在搜索引擎之上的最小 RAG 实现。

## 概念

本指南专注于文本数据的检索。我们将涵盖以下概念：
- 文档和文档加载器
- 文本分割器
- 嵌入
- 向量存储和检索器

## 设置

### 安装

本教程需要 `langchain-community` 和 `pypdf` 包：

```bash
pip install langchain-community pypdf
```

### LangSmith

您使用 LangChain 构建的许多应用程序将包含多个步骤和多次 LLM 调用。随着这些应用程序变得越来越复杂，能够检查链或智能体内部确切发生了什么变得至关重要。最好的方法是使用 LangSmith。

## 1. 文档和文档加载器

LangChain 实现了 Document 抽象，旨在表示文本单元和关联的元数据。它有三个属性：
- `page_content`: 表示内容的字符串
- `metadata`: 包含任意元数据的字典
- `id`: （可选）文档的字符串标识符

`metadata` 属性可以捕获有关文档来源、与其他文档的关系以及其他信息。

### 加载文档

让我们将 PDF 加载到一系列 Document 对象中。这是一个示例 PDF - 2023 年 Nike 的 10-k 文件。

```python
from langchain_community.document_loaders import PyPDFLoader

file_path = "./example_data/nike-10k-2023.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()
print(len(docs))  # 107
```

`PyPDFLoader` 为每个 PDF 页面加载一个 Document 对象。对于每个对象，我们可以轻松访问：
- 页面的字符串内容
- 包含文件名和页码的元数据

## 2. 分割

对于信息检索和下游问答目的，页面可能表示过于粗糙。我们可以为此目的使用文本分割器。

这里我们将使用一个基于字符分区的简单文本分割器。我们将文档分割为 1000 个字符的块，块之间有 200 个字符的重叠。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)
all_splits = text_splitter.split_documents(docs)
print(len(all_splits))  # 514
```

我们使用 `RecursiveCharacterTextSplitter`，它将使用常见分隔符（如换行符）递归分割文档，直到每个块达到适当大小。这是通用文本用例的推荐文本分割器。

我们设置 `add_start_index=True`，以便每个分割文档在初始文档中开始的字符索引作为元数据属性 `start_index` 保留。

## 3. 嵌入

向量搜索是存储和搜索非结构化数据（如非结构化文本）的常见方式。想法是存储与文本关联的数字向量。给定查询，我们可以将其嵌入为相同维度的向量，并使用向量相似性度量（如余弦相似性）来识别相关文本。

LangChain 支持来自数十个提供商的嵌入。这些模型指定了文本应如何转换为数字向量。

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_1 = embeddings.embed_query(all_splits[0].page_content)
vector_2 = embeddings.embed_query(all_splits[1].page_content)
assert len(vector_1) == len(vector_2)
print(f"Generated vectors of length {len(vector_1)}")
```

## 4. 向量存储

LangChain VectorStore 对象包含将文本和 Document 对象添加到存储的方法，以及使用各种相似性度量查询它们的方法。它们通常使用嵌入模型初始化，这些模型决定了文本数据如何转换为数字向量。

LangChain 包含与不同向量存储技术的一系列集成。

```python
from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embeddings)

# 索引文档
ids = vector_store.add_documents(documents=all_splits)
```

### 查询向量存储

一旦我们实例化了一个包含文档的 VectorStore，我们就可以查询它。

```python
# 基于与字符串查询的相似性返回文档
results = vector_store.similarity_search(
    "How many distribution centers does Nike have in the US?"
)
print(results[0])

# 异步查询
results = await vector_store.asimilarity_search("When was Nike incorporated?")
print(results[0])

# 返回分数
results = vector_store.similarity_search_with_score("What was Nike's revenue in 2023?")
doc, score = results[0]
print(f"Score: {score}")
print(doc)

# 基于与嵌入查询的相似性返回文档
embedding = embeddings.embed_query("How were Nike's margins impacted in 2023?")
results = vector_store.similarity_search_by_vector(embedding)
print(results[0])
```

## 5. 检索器

LangChain VectorStore 对象不继承 Runnable。LangChain 检索器是 Runnables，因此它们实现了一组标准方法（如同步和异步 invoke 和 batch 操作）。

虽然我们可以从向量存储构建检索器，但检索器也可以与非向量存储数据源（如外部 API）接口。

### 创建检索器

```python
from typing import List
from langchain_core.documents import Document
from langchain_core.runnables import chain

@chain
def retriever(query: str) -> List[Document]:
    return vector_store.similarity_search(query, k=1)

# 批量检索
results = retriever.batch([
    "How many distribution centers does Nike have in the US?",
    "When was Nike incorporated?",
])
```

或者，我们可以使用向量存储的内置检索器：

```python
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 1},
)

results = retriever.batch([
    "How many distribution centers does Nike have in the US?",
    "When was Nike incorporated?",
])
```

## 下一步

您现在已经看到了如何构建基于 PDF 文档的语义搜索引擎。要了解有关构建此类应用程序的更多信息，请查看 RAG 教程。

---

**原始文档URL**: https://docs.langchain.com/oss/python/langchain/knowledge-base
**整理时间**: 2025-11-10