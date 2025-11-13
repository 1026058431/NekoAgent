# LangChain 文档加载器集成指南

## 概述

文档加载器提供了一个标准接口，用于从不同来源（如 Slack、Notion 或 Google Drive）读取数据到 LangChain 的 Document 格式。这确保了无论来源如何，数据都可以一致地处理。

所有文档加载器都实现了 `BaseLoader` 接口。

## 接口

每个文档加载器可能定义自己的参数，但它们共享一个共同的 API：

- `.load()` - 一次性加载所有文档
- `.lazy_load()` - 惰性流式传输文档，对于大型数据集很有用

### 基本用法

```python
from langchain_community.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(
    ...  # 集成特定参数
)

# 加载所有文档
documents = loader.load()

# 对于大型数据集，惰性加载文档
for document in loader.lazy_load():
    print(document)
```

## 按类别分类

### 网页

以下文档加载器允许您加载网页。

| 文档加载器 | 描述 | 包 |
|------------|------|-----|
| WebBaseLoader | 使用 urllib 和 BeautifulSoup 加载和解析 HTML 网页 | `langchain-community` |
| Unstructured | 使用 Unstructured 加载和解析网页 | `langchain-community` |
| RecursiveURL | 从根 URL 递归抓取所有子链接 | `langchain-community` |
| Sitemap | 抓取给定站点地图上的所有页面 | `langchain-community` |
| Spider | 爬虫和抓取器，返回 LLM 就绪数据 | API |

### PDF

以下文档加载器允许您加载 PDF 文档。

| 文档加载器 | 描述 | 包 |
|------------|------|-----|
| PyPDFLoader | 使用 pypdf 加载和解析 PDF | `langchain-community` |
| Unstructured | 使用 Unstructured 的开源库加载 PDF | `langchain-community` |
| Amazon Textract | 使用 AWS API 加载 PDF | API |
| MathPix | 使用 MathPix 加载 PDF | `langchain-community` |
| PDFPlumber | 使用 PDFPlumber 加载 PDF 文件 | `langchain-community` |
| PyPDFDirectoryLoader | 加载包含 PDF 文件的目录 | `langchain-community` |

### 云提供商

以下文档加载器允许您从您喜欢的云提供商加载文档。

| 文档加载器 | 描述 | 包 |
|------------|------|-----|
| AWS S3 Directory | 从 AWS S3 目录加载文档 | `langchain-community` |
| AWS S3 File | 从 AWS S3 文件加载文档 | `langchain-community` |
| Azure Blob Storage | 从 Azure Blob Storage 加载文档 | `langchain-community` |
| Google Drive | 从 Google Drive 加载文档（仅限 Google Docs） | `langchain-community` |
| Google Cloud Storage | 从 GCS 存储桶加载文档 | `langchain-community` |

### 社交平台

以下文档加载器允许您从不同的社交媒体平台加载文档。

| 文档加载器 | 包 |
|------------|-----|
| TwitterTweetLoader | `langchain-community` |
| RedditPostsLoader | `langchain-community` |

### 消息服务

以下文档加载器允许您从不同的消息平台加载数据。

| 文档加载器 | 包 |
|------------|-----|
| TelegramChatFileLoader | `langchain-community` |
| WhatsAppChatLoader | `langchain-community` |
| DiscordChatLoader | `langchain-community` |
| FacebookChatLoader | `langchain-community` |

### 生产力工具

以下文档加载器允许您从常用生产力工具加载数据。

| 文档加载器 | 包 |
|------------|-----|
| FigmaFileLoader | `langchain-community` |
| NotionDirectoryLoader | `langchain-community` |
| SlackDirectoryLoader | `langchain-community` |
| QuipLoader | `langchain-community` |
| TrelloLoader | `langchain-community` |
| GithubFileLoader | `langchain-community` |

### 常见文件类型

以下文档加载器允许您从常见数据格式加载数据。

| 文档加载器 | 数据类型 | 包 |
|------------|----------|-----|
| CSVLoader | CSV 文件 | `langchain-community` |
| Unstructured | 多种文件类型 | `langchain-community` |
| JSONLoader | JSON 文件 | `langchain-community` |
| BSHTMLLoader | HTML 文件 | `langchain-community` |

## 常用加载器示例

### 1. 网页加载器

```python
from langchain_community.document_loaders import WebBaseLoader

# 加载单个网页
loader = WebBaseLoader("https://example.com")
documents = loader.load()

# 加载多个网页
loader = WebBaseLoader(["https://example1.com", "https://example2.com"])
documents = loader.load()
```

### 2. PDF 加载器

```python
from langchain_community.document_loaders import PyPDFLoader

# 加载单个 PDF
loader = PyPDFLoader("path/to/document.pdf")
documents = loader.load()

# 加载目录中的所有 PDF
from langchain_community.document_loaders import PyPDFDirectoryLoader

loader = PyPDFDirectoryLoader("path/to/pdf/directory/")
documents = loader.load()
```

### 3. 文本文件加载器

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("path/to/document.txt")
documents = loader.load()
```

### 4. CSV 加载器

```python
from langchain_community.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path="path/to/data.csv")
documents = loader.load()
```

### 5. JSON 加载器

```python
from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="path/to/data.json",
    jq_schema=".",  # 提取整个 JSON
    text_content=False
)
documents = loader.load()
```

## 高级用法

### 1. 惰性加载

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("large_document.pdf")

# 对于大型文档，使用惰性加载避免内存问题
for document in loader.lazy_load():
    # 处理每个文档
    print(f"页面内容: {document.page_content[:100]}...")
    print(f"元数据: {document.metadata}")
```

### 2. 自定义元数据

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("document.txt")
documents = loader.load()

# 添加自定义元数据
for doc in documents:
    doc.metadata.update({
        "source": "custom_source",
        "author": "unknown",
        "created_date": "2024-01-01"
    })
```

### 3. 多源加载

```python
from langchain_community.document_loaders import (
    WebBaseLoader, 
    PyPDFLoader, 
    TextLoader
)

# 从多个来源加载文档
all_documents = []

# 加载网页
web_loader = WebBaseLoader("https://example.com")
all_documents.extend(web_loader.load())

# 加载 PDF
pdf_loader = PyPDFLoader("document.pdf")
all_documents.extend(pdf_loader.load())

# 加载文本文件
text_loader = TextLoader("document.txt")
all_documents.extend(text_loader.load())
```

## 性能优化

### 1. 使用惰性加载处理大型数据集

```python
# 对于大型数据集，避免一次性加载所有内容
loader = SomeLargeDatasetLoader("large_dataset")

for document in loader.lazy_load():
    # 逐个处理文档
    process_document(document)
```

### 2. 并行加载

```python
from concurrent.futures import ThreadPoolExecutor

def load_document(loader):
    return loader.load()

loaders = [loader1, loader2, loader3]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(load_document, loaders))

all_documents = [doc for result in results for doc in result]
```

## 最佳实践

### 1. 错误处理

```python
try:
    loader = SomeLoader("path/to/file")
    documents = loader.load()
except Exception as e:
    print(f"加载文档时出错: {e}")
    # 处理错误或使用备用加载器
```

### 2. 内存管理

```python
# 对于大型文件，使用惰性加载
loader = LargeFileLoader("large_file.pdf")

for document in loader.lazy_load():
    # 处理每个文档后立即释放内存
    process_and_store(document)
    del document
```

### 3. 元数据管理

```python
# 始终添加有用的元数据
loader = SomeLoader("file")
documents = loader.load()

for doc in documents:
    doc.metadata.update({
        "loader_type": type(loader).__name__,
        "load_time": datetime.now().isoformat(),
        "file_size": os.path.getsize("file") if os.path.exists("file") else None
    })
```

## 常见问题

### Q: 如何处理损坏的文件？
A: 使用 try-except 块包装加载操作，并提供备用加载策略。

### Q: 如何优化大型文件的加载性能？
A: 使用惰性加载（`.lazy_load()`）并考虑并行处理。

### Q: 如何为不同文件类型选择正确的加载器？
A: 参考上面的分类表，根据文件类型和来源选择合适的加载器。

---

**原始文档URL**: https://docs.langchain.com/oss/python/integrations/document_loaders
**整理时间**: 2025-11-10