# LangChain 文本分割器集成指南

## 概述

文本分割器将大文档分解为较小的块，这些块可以单独检索并适合模型上下文窗口限制。有几种分割文档的策略，每种都有其自身的优势。

对于大多数用例，从 `RecursiveCharacterTextSplitter` 开始。它在保持上下文完整性和管理块大小之间提供了良好的平衡。这种默认策略开箱即用，只有在需要为特定应用程序微调性能时才应考虑调整它。

## 基于文本结构的分割

文本自然地组织成层次结构单元，如段落、句子和单词。我们可以利用这种固有结构来指导我们的分割策略，创建保持自然语言流程、在分割内保持语义连贯性并适应不同文本粒度级别的分割。

LangChain 的 `RecursiveCharacterTextSplitter` 实现了这个概念：

`RecursiveCharacterTextSplitter` 尝试保持较大的单元（例如，段落）完整。如果一个单元超过块大小，它会移动到下一个级别（例如，句子）。如果需要，这个过程会继续到单词级别。

### 示例用法

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0
)
texts = text_splitter.split_text(document)
```

### 可用的文本分割器

- **Recursively split text** - 递归分割文本

## 基于长度的分割

一种直观的策略是基于文档的长度进行分割。这种简单而有效的方法确保每个块不超过指定的大小限制。

### 基于长度分割的关键优势

- 直接实现
- 一致的块大小
- 易于适应不同的模型要求

### 基于长度分割的类型

1. **基于标记的分割**：基于标记数量分割文本，这在处理语言模型时很有用。
2. **基于字符的分割**：基于字符数量分割文本，这在不同类型的文本之间可能更一致。

### 示例实现

使用 LangChain 的 `CharacterTextSplitter` 进行基于标记的分割：

```python
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=100,
    chunk_overlap=0
)
texts = text_splitter.split_text(document)
```

### 可用的文本分割器

- **Split by tokens** - 按标记分割
- **Split by characters** - 按字符分割

## 基于文档结构的分割

某些文档具有固有结构，如 HTML、Markdown 或 JSON 文件。在这些情况下，基于文档结构进行分割是有益的，因为它通常自然地分组语义相关的文本。

### 基于结构分割的关键优势

- 保留文档的逻辑组织
- 在每个块内保持上下文
- 对于下游任务（如检索或摘要）可能更有效

### 基于结构分割的示例

- **Markdown**：基于标题分割（例如，`#`、`##`、`###`）
- **HTML**：使用标签分割
- **JSON**：按对象或数组元素分割
- **代码**：按函数、类或逻辑块分割

### 可用的文本分割器

- **Split Markdown** - 分割 Markdown
- **Split JSON** - 分割 JSON
- **Split code** - 分割代码
- **Split HTML** - 分割 HTML

## 提供者特定的分割器

- **WRITER** - WRITER 分割器

## 分割器选择指南

### 1. 通用文本
- **推荐**：`RecursiveCharacterTextSplitter`
- **优势**：平衡上下文保持和块大小管理
- **配置**：
  ```python
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200
  )
  ```

### 2. 代码文件
- **推荐**：基于语言的分割器
- **优势**：保持函数和类的完整性
- **配置**：
  ```python
  from langchain_text_splitters import Language
  from langchain_text_splitters import RecursiveCharacterTextSplitter
  
  python_splitter = RecursiveCharacterTextSplitter.from_language(
      language=Language.PYTHON,
      chunk_size=1000,
      chunk_overlap=200
  )
  ```

### 3. 结构化文档
- **推荐**：特定格式的分割器
- **优势**：利用文档的固有结构
- **配置**：
  ```python
  from langchain_text_splitters import MarkdownTextSplitter
  
  markdown_splitter = MarkdownTextSplitter(
      chunk_size=1000,
      chunk_overlap=200
  )
  ```

## 最佳实践

### 1. 块大小配置
- **一般文本**：500-1500 字符
- **代码**：1000-2000 字符
- **技术文档**：800-1200 字符

### 2. 重叠配置
- **推荐**：块大小的 10-20%
- **目的**：保持上下文连续性
- **示例**：对于 1000 字符的块，使用 100-200 字符的重叠

### 3. 分割策略
- **优先考虑语义完整性**：避免在句子中间分割
- **考虑下游任务**：检索、摘要、问答等
- **测试不同配置**：使用 LangSmith 评估分割效果

## 常见问题

### Q: 如何选择合适的分割器？
A: 从 `RecursiveCharacterTextSplitter` 开始，如果特定用例需要，再考虑专用分割器。

### Q: 块大小应该设置多大？
A: 取决于模型上下文窗口和文档类型。通常 500-1500 字符是一个好的起点。

### Q: 重叠有什么作用？
A: 重叠有助于保持上下文连续性，特别是在块边界处。

---

**原始文档URL**: https://docs.langchain.com/oss/python/integrations/splitters
**整理时间**: 2025-11-10