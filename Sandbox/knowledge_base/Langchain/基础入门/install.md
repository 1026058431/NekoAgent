# LangChain 安装指南

## 安装 LangChain 包

### 使用 pip 安装
```bash
pip install -U langchain
```

### 使用 uv 安装
```bash
uv add langchain
```

## 集成包安装

LangChain 提供了与数百个 LLM 和数千个其他集成的连接。这些集成位于独立的提供商包中。

### 安装 OpenAI 集成
```bash
pip install -U langchain-openai
```

### 安装 Anthropic 集成
```bash
pip install -U langchain-anthropic
```

## 其他常用集成

- **Google**: `langchain-google-genai`
- **Hugging Face**: `langchain-huggingface`
- **Azure OpenAI**: `langchain-openai`
- **Cohere**: `langchain-cohere`
- **Groq**: `langchain-groq`

## 环境变量设置

在使用特定模型提供商之前，需要设置相应的 API 密钥：

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Google
export GOOGLE_API_KEY="your-google-api-key"
```

## 验证安装

安装完成后，可以通过以下方式验证安装：

```python
import langchain
print(f"LangChain version: {langchain.__version__}")
```

## 升级到最新版本

要升级到最新版本的 LangChain：

```bash
pip install -U langchain
```

## 注意事项

- LangChain v1.0 是一个重大更新，包含了对所有链和智能体的完全重构
- 对于仍在使用旧版 LangChain 链/智能体且不想升级的用户，可以继续使用 `langchain-classic` 包
- 建议查看 v1.0 发布说明和迁移指南以了解完整的变更列表和升级说明# LangChain 安装指南

## 安装 LangChain 包

### 使用 pip 安装
```bash
pip install -U langchain
```

### 使用 uv 安装
```bash
uv add langchain
```

## 集成包安装

LangChain 提供了与数百个 LLM 和数千个其他集成的连接。这些集成位于独立的提供商包中。

### 安装 OpenAI 集成
```bash
pip install -U langchain-openai
```

### 安装 Anthropic 集成
```bash
pip install -U langchain-anthropic
```

## 其他常用集成

- **Google**: `langchain-google-genai`
- **Hugging Face**: `langchain-huggingface`
- **Azure OpenAI**: `langchain-openai`
- **Cohere**: `langchain-cohere`
- **Groq**: `langchain-groq`

## 环境变量设置

在使用特定模型提供商之前，需要设置相应的 API 密钥：

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Google
export GOOGLE_API_KEY="your-google-api-key"
```

## 验证安装

安装完成后，可以通过以下方式验证安装：

```python
import langchain
print(f"LangChain version: {langchain.__version__}")
```

## 升级到最新版本

要升级到最新版本的 LangChain：

```bash
pip install -U langchain
```

## 注意事项

- LangChain v1.0 是一个重大更新，包含了对所有链和智能体的完全重构
- 对于仍在使用旧版 LangChain 链/智能体且不想升级的用户，可以继续使用 `langchain-classic` 包
- 建议查看 v1.0 发布说明和迁移指南以了解完整的变更列表和升级说明

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/install