# LangChain 检索器集成指南

## 概述

检索器是一个接口，给定非结构化查询时返回文档。它比向量存储更通用。检索器不需要能够存储文档，只需要返回（或检索）它们。

检索器可以从向量存储创建，但也足够广泛，包括 Wikipedia 搜索和 Amazon Kendra。检索器接受字符串查询作为输入，并返回文档列表作为输出。

**注意**：所有向量存储都可以转换为检索器。请参阅向量存储集成文档以获取可用的向量存储。

本页面列出了通过子类化 `BaseRetriever` 实现的自定义检索器。

## 自带文档检索器

以下检索器允许您索引和搜索自定义文档语料库。

| 检索器 | 自托管 | 云服务 | 包 |
|--------|--------|--------|-----|
| AmazonKnowledgeBasesRetriever | ✅ | ❌ | `langchain-aws` |
| AzureAISearchRetriever | ✅ | ❌ | `langchain-community` |
| ElasticsearchRetriever | ✅ | ❌ | `langchain-elasticsearch` |
| VertexAISearchRetriever | ✅ | ❌ | `langchain-google-community` |

## 外部索引检索器

以下检索器将搜索外部索引（例如，从互联网数据或类似数据构建）。

| 检索器 | 来源 | 包 |
|--------|------|-----|
| ArxivRetriever | 学术文章 (arxiv.org) | `langchain-community` |
| TavilySearchAPIRetriever | 互联网搜索 | `langchain-community` |
| WikipediaRetriever | Wikipedia 文章 | `langchain-community` |

## 所有检索器列表

以下是 LangChain 支持的所有检索器的完整列表：

### A
- **Activeloop Deep Memory** - 深度记忆检索器
- **Amazon Kendra** - Amazon Kendra 检索器
- **Arcee** - Arcee 检索器
- **Arxiv** - 学术论文检索器
- **AskNews** - 新闻检索器

### B
- **Azure AI Search** - Azure AI 搜索检索器
- **Bedrock (Knowledge Bases)** - AWS Bedrock 知识库检索器
- **BM25** - BM25 检索算法
- **Box** - Box 存储检索器
- **BREEBS (Open Knowledge)** - 开放知识检索器

### C
- **Chaindesk** - Chaindesk 检索器
- **ChatGPT plugin** - ChatGPT 插件检索器
- **Cognee** - Cognee 检索器
- **Cohere reranker** - Cohere 重排序器
- **Cohere RAG** - Cohere RAG 检索器
- **Contextual AI Reranker** - 上下文 AI 重排序器

### D
- **Dappier** - Dappier 检索器
- **DocArray** - DocArray 检索器
- **Dria** - Dria 检索器

### E
- **ElasticSearch BM25** - ElasticSearch BM25 检索器
- **Elasticsearch** - Elasticsearch 检索器
- **Embedchain** - Embedchain 检索器

### F
- **FlashRank reranker** - FlashRank 重排序器
- **Fleet AI Context** - Fleet AI 上下文检索器

### G
- **Galaxia** - Galaxia 检索器
- **Google Drive** - Google Drive 检索器
- **Google Vertex AI Search** - Google Vertex AI 搜索检索器
- **Graph RAG** - 图 RAG 检索器
- **GreenNode** - GreenNode 检索器

### I
- **IBM watsonx.ai** - IBM watsonx.ai 检索器

### J
- **JaguarDB Vector Database** - JaguarDB 向量数据库检索器

### K
- **Kay.ai** - Kay.ai 检索器
- **Kinetica Vectorstore** - Kinetica 向量存储检索器
- **kNN** - k-最近邻检索器

### L
- **LinkupSearchRetriever** - Linkup 搜索检索器
- **LLMLingua Document Compressor** - LLMLingua 文档压缩器
- **LOTR (Merger Retriever)** - LOTR 合并检索器

### M
- **Metal** - Metal 检索器
- **NanoPQ (Product Quantization)** - NanoPQ 产品量化检索器

### N
- **Nebius** - Nebius 检索器
- **needle** - needle 检索器
- **Nimble** - Nimble 检索器

### O
- **Outline** - Outline 检索器

### P
- **Permit** - Permit 检索器
- **Pinecone Hybrid Search** - Pinecone 混合搜索检索器
- **Pinecone Rerank** - Pinecone 重排序器
- **PubMed** - PubMed 检索器

### Q
- **Qdrant Sparse Vector** - Qdrant 稀疏向量检索器

### R
- **RAGatouille** - RAGatouille 检索器
- **RePhraseQuery** - 查询重写检索器
- **Rememberizer** - Rememberizer 检索器

### S
- **SEC filing** - SEC 文件检索器
- **SVM** - 支持向量机检索器

### T
- **TavilySearchAPI** - Tavily 搜索 API 检索器
- **TF-IDF** - TF-IDF 检索器

### V
- **ValyuContext** - Valyu 上下文检索器
- **Vectorize** - Vectorize 检索器
- **Vespa** - Vespa 检索器

### W
- **Wikipedia** - Wikipedia 检索器

### Y
- **You.com** - You.com 检索器

### Z
- **Zep Cloud** - Zep 云检索器
- **Zep Open Source** - Zep 开源检索器
- **Zotero** - Zotero 检索器

## 使用示例

### 从向量存储创建检索器

```python
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

# 初始化向量存储
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)

# 转换为检索器
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# 使用检索器
results = retriever.invoke("What is machine learning?")
```

### 使用外部检索器

```python
from langchain_community.retrievers import WikipediaRetriever

# 创建 Wikipedia 检索器
wiki_retriever = WikipediaRetriever()

# 搜索 Wikipedia
results = wiki_retriever.invoke("Artificial Intelligence")
```

## 检索器类型

### 1. 向量存储检索器
- 基于向量相似度的检索
- 支持多种向量存储后端
- 可配置搜索参数

### 2. 关键词检索器
- 基于关键词匹配
- 如 BM25、TF-IDF
- 适合精确术语匹配

### 3. 外部 API 检索器
- 连接到外部搜索服务
- 如 Wikipedia、Arxiv、Tavily
- 提供实时外部数据

### 4. 混合检索器
- 结合多种检索策略
- 如 LOTR (Merger Retriever)
- 提供更好的召回率和精度

## 最佳实践

1. **选择合适的检索器**：根据数据源和需求选择
2. **配置搜索参数**：调整 k 值、相似度阈值等
3. **考虑混合检索**：结合多种检索策略提高效果
4. **监控性能**：使用 LangSmith 跟踪检索性能

---

**原始文档URL**: https://docs.langchain.com/oss/python/integrations/retrievers
**整理时间**: 2025-11-10