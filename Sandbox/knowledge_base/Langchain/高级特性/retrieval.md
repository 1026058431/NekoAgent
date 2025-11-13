# 检索

大型语言模型（LLMs）功能强大，但它们有两个关键限制：
- **有限上下文** - 它们无法一次性摄取整个语料库
- **静态知识** - 它们的训练数据在某个时间点被冻结

检索通过在查询时获取相关的外部知识来解决这些问题。这是检索增强生成（RAG）的基础：用上下文特定的信息增强LLM的答案。

## 构建知识库

知识库是在检索期间使用的文档或结构化数据的存储库。如果你需要自定义知识库，可以使用LangChain的文档加载器和向量存储从你自己的数据构建一个。

如果你已经有知识库（例如，SQL数据库、CRM或内部文档系统），则不需要重建它。你可以：
- 将其作为工具连接到智能体进行Agentic RAG
- 查询它并将检索到的内容作为上下文提供给LLM（2-Step RAG）

查看以下教程以构建可搜索的知识库和最小RAG工作流：

**教程：语义搜索**

学习如何使用LangChain的文档加载器、嵌入和向量存储从你自己的数据创建可搜索的知识库。在本教程中，你将构建一个基于PDF的搜索引擎，能够检索与查询相关的段落。你还将在此引擎之上实现一个最小RAG工作流，以了解外部知识如何集成到LLM推理中。

[了解更多](https://docs.langchain.com/oss/python/langchain/tutorials/semantic-search)

## 从检索到RAG

检索允许LLMs在运行时访问相关上下文。但大多数现实世界的应用程序更进一步：它们将检索与生成集成，以产生有根据的、上下文感知的答案。这是检索增强生成（RAG）的核心思想。

检索管道成为结合搜索与生成的更广泛系统的基础。

## 检索管道

典型的检索工作流如下所示：

```
文档加载器 → 文本分割器 → 嵌入模型 → 向量存储 → 检索器
```

每个组件都是模块化的：你可以交换加载器、分割器、嵌入或向量存储，而无需重写应用程序的逻辑。

## 构建块

### 文档加载器
从外部源（Google Drive、Slack、Notion等）摄取数据，返回标准化的Document对象。

[了解更多](https://docs.langchain.com/oss/python/langchain/document-loaders)

### 文本分割器
将大文档分解为较小的块，这些块可以单独检索并适合模型的上下文窗口。

[了解更多](https://docs.langchain.com/oss/python/langchain/text-splitters)

### 嵌入模型
嵌入模型将文本转换为数字向量，使得具有相似含义的文本在该向量空间中彼此靠近。

[了解更多](https://docs.langchain.com/oss/python/langchain/embeddings)

### 向量存储
用于存储和搜索嵌入的专门数据库。

[了解更多](https://docs.langchain.com/oss/python/langchain/vector-stores)

### 检索器
检索器是一个接口，给定非结构化查询时返回文档。

[了解更多](https://docs.langchain.com/oss/python/langchain/retrievers)

## RAG架构

RAG可以根据系统的需求以多种方式实现。我们在下面的部分中概述每种类型。

| 架构 | 描述 | 控制 | 灵活性 | 延迟 | 示例用例 |
|------|------|------|--------|------|----------|
| **2-Step RAG** | 检索总是在生成之前发生。简单且可预测 | ✅ 高 | ❌ 低 | ⚡ 快速 | 常见问题解答、文档机器人 |
| **Agentic RAG** | LLM驱动的智能体在推理期间决定何时以及如何检索 | ❌ 低 | ✅ 高 | ⏳ 可变 | 具有访问多个工具的研究助手 |
| **Hybrid** | 结合两种方法的特性，具有验证步骤 | ⚖️ 中等 | ⚖️ 中等 | ⏳ 可变 | 具有质量验证的领域特定问答 |

**延迟**：延迟在2-Step RAG中通常更可预测，因为LLM调用的最大数量是已知且有上限的。这种可预测性假设LLM推理时间是主导因素。然而，现实世界的延迟也可能受到检索步骤性能的影响——例如API响应时间、网络延迟或数据库查询——这些可能因使用的工具和基础设施而异。

## 2-step RAG

在2-Step RAG中，检索步骤总是在生成步骤之前执行。这种架构简单且可预测，适用于许多应用程序，其中检索相关文档是生成答案的明确先决条件。

**教程：检索增强生成（RAG）**

了解如何构建一个能够基于你的数据回答问题的问答聊天机器人，使用检索增强生成。本教程介绍了两种方法：
- 使用灵活工具运行搜索的RAG智能体——非常适合通用用途
- 每个查询只需要一次LLM调用的2-step RAG链——对于更简单的任务快速高效

[了解更多](https://docs.langchain.com/oss/python/langchain/tutorials/rag)

## Agentic RAG

Agentic Retrieval-Augmented Generation（RAG）结合了检索增强生成与基于智能体的推理的优势。不是在回答之前检索文档，而是由智能体（由LLM驱动）逐步推理，并在交互期间决定何时以及如何检索信息。

智能体启用RAG行为唯一需要的是访问一个或多个可以获取外部知识的工具——例如文档加载器、Web API或数据库查询。

```python
import requests
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

@tool
def fetch_url(url: str) -> str:
    """Fetch text content from a URL"""
    response = requests.get(url, timeout=10.0)
    response.raise_for_status()
    return response.text

system_prompt = """\\
Use fetch_url when you need to fetch information from a web-page; quote relevant snippets.
"""

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[fetch_url],  # 用于检索的工具
    system_prompt=system_prompt,
)
```

**扩展示例：用于LangGraph的llms.txt的Agentic RAG**

此示例实现了一个Agentic RAG系统，以帮助用户查询LangGraph文档。智能体首先加载llms.txt，其中列出了可用的文档URL，然后可以根据用户的问题动态使用 `fetch_documentation` 工具来检索和处理相关内容。

```python
import requests
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from markdownify import markdownify

ALLOWED_DOMAINS = ["https://langchain-ai.github.io/"]
LLMS_TXT = 'https://langchain-ai.github.io/langgraph/llms.txt'

@tool
def fetch_documentation(url: str) -> str:
    """Fetch and convert documentation from a URL"""
    if not any(url.startswith(domain) for domain in ALLOWED_DOMAINS):
        return (
            "Error: URL not allowed. "
            f"Must start with one of: {', '.join(ALLOWED_DOMAINS)}"
        )
    
    response = requests.get(url, timeout=10.0)
    response.raise_for_status()
    return markdownify(response.text)

# 我们将获取llms.txt的内容，因此这可以
# 提前完成，而不需要LLM请求。
llms_txt_content = requests.get(LLMS_TXT).text

# 智能体的系统提示
system_prompt = f"""
You are an expert Python developer and technical assistant.
Your primary role is to help users with questions about LangGraph and related tools.

Instructions:
1. If a user asks a question you're unsure about — or one that likely involves API usage, behavior, or configuration — you MUST use the `fetch_documentation` tool to consult the relevant docs.
2. When citing documentation, summarize clearly and include relevant context from the content.
3. Do not use any URLs outside of the allowed domain.
4. If a documentation fetch fails, tell the user and proceed with your best expert understanding.

You can access official documentation from the following approved sources:
{llms_txt_content}

You MUST consult the documentation to get up to date documentation before answering a user's question about LangGraph.

Your answers should be clear, concise, and technically accurate.
"""

tools = [fetch_documentation]
model = init_chat_model("claude-sonnet-4-0", max_tokens=32_000)
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
    name="Agentic RAG",
)

response = agent.invoke({
    'messages': [
        HumanMessage(content=(
            "Write a short example of a langgraph agent using the "
            "prebuilt create react agent. the agent should be able "
            "to look up stock pricing information."
        ))
    ]
})

print(response['messages'][-1].content)
```

**教程：检索增强生成（RAG）**

了解如何构建一个能够基于你的数据回答问题的问答聊天机器人，使用检索增强生成。本教程介绍了两种方法：
- 使用灵活工具运行搜索的RAG智能体——非常适合通用用途
- 每个查询只需要一次LLM调用的2-step RAG链——对于更简单的任务快速高效

[了解更多](https://docs.langchain.com/oss/python/langchain/tutorials/rag)

## Hybrid RAG

Hybrid RAG结合了2-Step和Agentic RAG的特性。它引入了中间步骤，如查询预处理、检索验证和后生成检查。这些系统比固定管道提供更多灵活性，同时保持对执行的一些控制。

典型组件包括：
- **查询增强**：修改输入问题以提高检索质量。这可能涉及重写不清楚的查询、生成多个变体或用额外上下文扩展查询。
- **检索验证**：评估检索到的文档是否相关且充分。如果不是，系统可能会优化查询并再次检索。
- **答案验证**：检查生成的答案的准确性、完整性和与源内容的一致性。如果需要，系统可以重新生成或修订答案。

架构通常支持这些步骤之间的多次迭代：

```
查询 → 增强 → 检索 → 验证 → 生成 → 验证 → 输出
```

这种架构适用于：
- 具有模糊或未充分指定查询的应用程序
- 需要验证或质量控制步骤的系统
- 涉及多个来源或迭代优化的工作流

**教程：具有自我纠正的Agentic RAG**

结合智能体推理与检索和自我纠正的Hybrid RAG示例。

[了解更多](https://docs.langchain.com/oss/python/langchain/tutorials/agentic-rag-self-correction)---

**原始文档URL**: https://docs.langchain.com/oss/python/langchain/retrieval