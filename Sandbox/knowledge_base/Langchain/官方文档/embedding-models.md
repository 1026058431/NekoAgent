# LangChain 文本嵌入模型集成指南

## 概述

本概述涵盖基于文本的嵌入模型。LangChain 目前不支持多模态嵌入。

嵌入模型将原始文本（如句子、段落或推文）转换为固定长度的数字向量，捕获其语义含义。这些向量允许机器基于含义而不是精确的单词来比较和搜索文本。

在实践中，这意味着具有相似思想的文本在向量空间中彼此靠近放置。例如，嵌入不仅可以匹配短语"机器学习"，还可以显示讨论相关概念的文档，即使使用了不同的措辞。

## 工作原理

### 向量化
模型将每个输入字符串编码为高维向量。

### 相似性评分
使用数学度量比较向量，以衡量底层文本的密切程度。

## 相似性度量

几种度量通常用于比较嵌入：

- **余弦相似度** - 测量两个向量之间的角度
- **欧几里得距离** - 测量点之间的直线距离
- **点积** - 测量一个向量在另一个向量上的投影程度

### 计算余弦相似度示例

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    dot = np.dot(vec1, vec2)
    return dot / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

similarity = cosine_similarity(query_embedding, document_embedding)
print("Cosine Similarity:", similarity)
```

## 接口

LangChain 通过 `Embeddings` 接口为文本嵌入模型（例如 OpenAI、Cohere、Hugging Face）提供标准接口。

### 两个主要方法

- `embed_documents(texts: List[str]) -> List[List[float]]`：嵌入文档列表
- `embed_query(text: str) -> List[float]`：嵌入单个查询

该接口允许查询和文档使用不同的策略进行嵌入，尽管大多数提供者在实践中以相同的方式处理它们。

## 顶级集成

| 模型 | 包 |
|------|-----|
| OpenAIEmbeddings | `langchain-openai` |
| AzureOpenAIEmbeddings | `langchain-openai` |
| GoogleGenerativeAIEmbeddings | `langchain-google-genai` |
| OllamaEmbeddings | `langchain-ollama` |
| TogetherEmbeddings | `langchain-together` |
| FireworksEmbeddings | `langchain-fireworks` |
| MistralAIEmbeddings | `langchain-mistralai` |
| CohereEmbeddings | `langchain-cohere` |
| NomicEmbeddings | `langchain-nomic` |
| FakeEmbeddings | `langchain-core` |
| DatabricksEmbeddings | `databricks-langchain` |
| WatsonxEmbeddings | `langchain-ibm` |
| NVIDIAEmbeddings | `langchain-nvidia` |
| AimlapiEmbeddings | `langchain-aimlapi` |

## 缓存

嵌入可以被存储或临时缓存，以避免需要重新计算它们。

可以使用 `CacheBackedEmbeddings` 来缓存嵌入。这个包装器将嵌入存储在键值存储中，其中文本被哈希，哈希用作缓存中的键。

初始化 `CacheBackedEmbeddings` 的主要支持方式是从 `from_bytes_store`。它接受以下参数：

- `underlying_embedder`：用于嵌入的嵌入器
- `document_embedding_cache`：用于缓存文档嵌入的任何 ByteStore
- `batch_size`：（可选，默认为 None）存储更新之间要嵌入的文档数量
- `namespace`：（可选，默认为 ""）用于文档缓存的命名空间。有助于避免冲突（例如，将其设置为嵌入模型名称）
- `query_embedding_cache`：（可选，默认为 None）用于缓存查询嵌入的 ByteStore，或 True 以重用与 `document_embedding_cache` 相同的存储

### 缓存示例

```python
import time
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
from langchain_core.vectorstores import InMemoryVectorStore

# 创建底层嵌入模型
underlying_embeddings = ...  # 例如，OpenAIEmbeddings(), HuggingFaceEmbeddings() 等

# 存储将嵌入持久化到本地文件系统
# 这不适用于生产用途，但对本地存储很有用
store = LocalFileStore("./cache")

cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings,
    store,
    namespace=underlying_embeddings.model
)

# 示例：缓存查询嵌入
tic = time.time()
print(cached_embedder.embed_query("Hello, world!"))
print(f"First call took: {time.time() - tic:.2f} seconds")

# 后续调用使用缓存
tic = time.time()
print(cached_embedder.embed_query("Hello, world!"))
print(f"Second call took: {time.time() - tic:.2f} seconds")
```

在生产中，您通常会使用更健壮的持久存储，例如数据库或云存储。请参阅存储集成以获取选项。

## 所有嵌入模型

以下是 LangChain 支持的所有嵌入模型的完整列表：

### A
- **Aleph Alpha** - Aleph Alpha 嵌入模型
- **Anyscale** - Anyscale 嵌入模型
- **Ascend** - Ascend 嵌入模型
- **AIML API** - AIML API 嵌入模型
- **AwaDB** - AwaDB 嵌入模型
- **AzureOpenAI** - Azure OpenAI 嵌入模型

### B
- **Baichuan Text Embeddings** - 百川文本嵌入
- **Baidu Qianfan** - 百度千帆嵌入
- **Baseten** - Baseten 嵌入模型
- **Bedrock** - AWS Bedrock 嵌入模型
- **BGE on Hugging Face** - Hugging Face 上的 BGE 嵌入
- **Bookend AI** - Bookend AI 嵌入模型

### C
- **Clarifai** - Clarifai 嵌入模型
- **Cloudflare Workers AI** - Cloudflare Workers AI 嵌入
- **Clova Embeddings** - Clova 嵌入
- **Cohere** - Cohere 嵌入模型

### D
- **DashScope** - 达摩院 DashScope 嵌入
- **Databricks** - Databricks 嵌入模型
- **DeepInfra** - DeepInfra 嵌入模型

### E
- **EDEN AI** - EDEN AI 嵌入模型
- **Elasticsearch** - Elasticsearch 嵌入模型
- **Embaas** - Embaas 嵌入模型

### F
- **Fake Embeddings** - 假嵌入（用于测试）
- **FastEmbed by Qdrant** - Qdrant 的 FastEmbed
- **Fireworks** - Fireworks 嵌入模型

### G
- **Google Gemini** - Google Gemini 嵌入
- **Google Vertex AI** - Google Vertex AI 嵌入
- **GPT4All** - GPT4All 嵌入模型
- **Gradient** - Gradient 嵌入模型
- **GreenNode** - GreenNode 嵌入模型

### H
- **Hugging Face** - Hugging Face 嵌入模型

### I
- **IBM watsonx.ai** - IBM watsonx.ai 嵌入
- **Infinity** - Infinity 嵌入模型
- **Instruct Embeddings** - 指令嵌入
- **IPEX-LLM CPU** - IPEX-LLM CPU 嵌入
- **IPEX-LLM GPU** - IPEX-LLM GPU 嵌入
- **Intel Extension for Transformers** - Intel 转换器扩展

### J
- **Jina** - Jina 嵌入模型
- **John Snow Labs** - John Snow Labs 嵌入

### L
- **LASER** - LASER 嵌入模型
- **Lindorm** - Lindorm 嵌入模型
- **Llama.cpp** - Llama.cpp 嵌入
- **LLMRails** - LLMRails 嵌入模型
- **LocalAI** - LocalAI 嵌入模型

### M
- **MiniMax** - MiniMax 嵌入模型
- **MistralAI** - MistralAI 嵌入模型
- **Model2Vec** - Model2Vec 嵌入模型
- **ModelScope** - 魔搭 ModelScope 嵌入
- **MosaicML** - MosaicML 嵌入模型

### N
- **Naver** - Naver 嵌入模型
- **Nebius** - Nebius 嵌入模型
- **Netmind** - Netmind 嵌入模型
- **NLP Cloud** - NLP Cloud 嵌入
- **Nomic** - Nomic 嵌入模型
- **NVIDIA NIMs** - NVIDIA NIMs 嵌入

### O
- **Oracle Cloud Infrastructure** - Oracle 云基础设施嵌入
- **Ollama** - Ollama 嵌入模型
- **OpenClip** - OpenClip 嵌入
- **OpenAI** - OpenAI 嵌入模型
- **OpenVINO** - OpenVINO 嵌入
- **Optimum Intel** - Optimum Intel 嵌入
- **Oracle AI Vector Search** - Oracle AI 向量搜索
- **OVHcloud** - OVHcloud 嵌入

### P
- **Pinecone Embeddings** - Pinecone 嵌入
- **PredictionGuard** - PredictionGuard 嵌入
- **PremAI** - PremAI 嵌入模型

### S
- **SageMaker** - SageMaker 嵌入模型
- **SambaNova** - SambaNova 嵌入模型
- **Self Hosted** - 自托管嵌入模型
- **Sentence Transformers** - 句子转换器
- **Solar** - Solar 嵌入模型
- **SpaCy** - SpaCy 嵌入
- **SparkLLM** - SparkLLM 嵌入模型

### T
- **TensorFlow Hub** - TensorFlow Hub 嵌入
- **Text Embeddings Inference** - 文本嵌入推理
- **TextEmbed** - TextEmbed 嵌入
- **Titan Takeoff** - Titan Takeoff 嵌入
- **Together AI** - Together AI 嵌入

### U
- **Upstage** - Upstage 嵌入模型

### V
- **Volc Engine** - 火山引擎嵌入
- **Voyage AI** - Voyage AI 嵌入

### X
- **Xinference** - Xinference 嵌入

### Y
- **YandexGPT** - YandexGPT 嵌入

### Z
- **ZhipuAI** - 智谱AI 嵌入

## 使用示例

### 基本嵌入使用

```python
from langchain_openai import OpenAIEmbeddings

# 初始化嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 嵌入文档
documents = ["This is a document", "This is another document"]
doc_embeddings = embeddings.embed_documents(documents)

# 嵌入查询
query = "What is this about?"
query_embedding = embeddings.embed_query(query)
```

### 缓存嵌入

```python
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore

# 创建缓存嵌入器
store = LocalFileStore("./embedding_cache")
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
    embeddings,
    store,
    namespace="openai_embeddings"
)
```

## 最佳实践

1. **选择合适的嵌入模型**：根据语言、领域和性能要求选择
2. **使用缓存**：对于重复查询，使用缓存提高性能
3. **批量处理**：对于大量文档，使用批量嵌入
4. **监控性能**：使用 LangSmith 跟踪嵌入性能

---

**原始文档URL**: https://docs.langchain.com/oss/python/integrations/text_embedding
**整理时间**: 2025-11-10