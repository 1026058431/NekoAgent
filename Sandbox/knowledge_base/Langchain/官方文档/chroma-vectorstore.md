# LangChain ChromaDB 向量存储集成指南

## 概述

向量存储存储嵌入数据并执行相似性搜索。

## 接口

LangChain 为向量存储提供统一接口，允许您：
- `add_documents` - 将文档添加到存储
- `delete` - 按 ID 删除存储的文档
- `similarity_search` - 查询语义相似的文档

这种抽象允许您在不同的实现之间切换，而无需更改应用程序逻辑。

## 初始化

要初始化向量存储，请为其提供嵌入模型：

```python
from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embedding=SomeEmbeddingModel())
```

## 添加文档

添加 `Document` 对象（包含 `page_content` 和可选的 `metadata`）：

```python
vector_store.add_documents(documents=[doc1, doc2], ids=["id1", "id2"])
```

## 删除文档

通过指定 ID 删除：

```python
vector_store.delete(ids=["id1"])
```

## 相似性搜索

使用 `similarity_search` 发出语义查询，返回最接近的嵌入文档：

```python
similar_docs = vector_store.similarity_search("your query here")
```

许多向量存储支持参数如：
- `k` - 要返回的结果数量
- `filter` - 基于元数据的条件过滤

## 相似性度量和索引

嵌入相似性可以使用以下方式计算：
- 余弦相似度
- 欧几里得距离
- 点积

高效搜索通常使用索引方法，如 HNSW（分层可导航小世界），尽管具体细节取决于向量存储。

## 元数据过滤

通过元数据（例如，来源、日期）过滤可以优化搜索结果：

```python
vector_store.similarity_search(
    "query", 
    k=3, 
    filter={"source": "tweets"}
)
```

## ChromaDB 集成

### 安装

```bash
pip install -qU langchain-chroma
```

### 初始化

```python
from langchain_chroma import Chroma

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",  # 本地保存数据的位置，如果不需要请移除
)
```

### 配置参数

- `collection_name`：集合名称
- `embedding_function`：嵌入函数
- `persist_directory`：持久化目录（可选）
- `client_settings`：客户端设置（可选）
- `collection_metadata`：集合元数据（可选）

## 与 Ollama 嵌入集成

```python
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# 使用 Ollama 嵌入
embeddings = OllamaEmbeddings(model="qwen3-embedding")

# 初始化 ChromaDB
vector_store = Chroma(
    collection_name="my_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
```

## 与 Sentence Transformers 集成

```python
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# 使用 ChromaDB 自带的 Sentence Transformers
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 初始化 ChromaDB
vector_store = Chroma(
    collection_name="my_collection",
    embedding_function=embeddings
)
```

## 完整使用示例

### 1. 基本使用

```python
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# 初始化嵌入和向量存储
embeddings = OllamaEmbeddings(model="qwen3-embedding")
vector_store = Chroma(
    collection_name="example",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# 创建文档
documents = [
    Document(page_content="机器学习是人工智能的一个子领域", metadata={"source": "wiki"}),
    Document(page_content="深度学习是机器学习的一个分支", metadata={"source": "blog"})
]

# 添加文档
vector_store.add_documents(documents)

# 搜索
results = vector_store.similarity_search("什么是机器学习？", k=2)
for doc in results:
    print(f"内容: {doc.page_content}")
    print(f"元数据: {doc.metadata}")
```

### 2. 带过滤的搜索

```python
# 带元数据过滤的搜索
results = vector_store.similarity_search(
    "人工智能", 
    k=3, 
    filter={"source": "wiki"}
)
```

### 3. 删除操作

```python
# 获取文档ID
all_docs = vector_store.get()
doc_ids = [doc.id for doc in all_docs['documents']]

# 删除特定文档
if doc_ids:
    vector_store.delete(ids=[doc_ids[0]])
```

## 性能优化

### 1. 批量添加文档

```python
# 批量添加大量文档
vector_store.add_documents(documents=large_document_list)
```

### 2. 使用持久化

```python
# 启用持久化以保存数据
vector_store = Chroma(
    collection_name="persistent_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_persistent"
)
```

### 3. 配置搜索参数

```python
# 优化搜索性能
results = vector_store.similarity_search(
    "query",
    k=5,
    filter={"category": "technical"},
    # ChromaDB 特定参数
    n_results=10  # 内部检索更多结果进行过滤
)
```

## 与其他向量存储对比

| 特性 | ChromaDB | FAISS | Pinecone |
|------|----------|-------|----------|
| 本地部署 | ✅ | ✅ | ❌ |
| 持久化 | ✅ | ❌ | ✅ |
| 元数据过滤 | ✅ | ❌ | ✅ |
| 云服务 | ❌ | ❌ | ✅ |
| 安装复杂度 | 低 | 中 | 低 |

## 最佳实践

1. **选择合适的嵌入模型**：
   - 生产环境：Ollama (`qwen3-embedding`)
   - 开发测试：ChromaDB 自带 Sentence Transformers

2. **配置持久化**：
   - 生产环境启用持久化
   - 定期备份数据

3. **优化搜索参数**：
   - 根据数据量调整 `k` 值
   - 使用元数据过滤提高精度

4. **监控性能**：
   - 使用 LangSmith 跟踪搜索性能
   - 监控内存使用情况

## 故障排除

### 常见问题

1. **内存不足**：
   - 减少批量添加的文档数量
   - 使用更轻量的嵌入模型

2. **搜索性能慢**：
   - 调整 `k` 值
   - 使用元数据过滤减少搜索空间

3. **持久化问题**：
   - 检查目录权限
   - 确保有足够的磁盘空间

---

**原始文档URL**: https://docs.langchain.com/oss/python/integrations/vectorstores/index#chroma
**整理时间**: 2025-11-10