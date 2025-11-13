# LangChain 概览

## LangChain v1.0 现已发布！

LangChain 是构建由 LLM 驱动的智能体和应用程序的最简单方式。只需不到 10 行代码，您就可以连接到 OpenAI、Anthropic、Google 等模型提供商。

## 核心优势

### 标准模型接口
不同提供商有独特的 API 来与模型交互，包括响应格式。LangChain 标准化了与模型的交互方式，使您可以无缝切换提供商并避免锁定。

### 易于使用、高度灵活的智能体
LangChain 的智能体抽象设计易于上手，让您可以在不到 10 行代码中构建一个简单的智能体。但也提供了足够的灵活性，让您可以进行所有您想要的情境工程。

### 基于 LangGraph 构建
LangChain 的智能体基于 LangGraph 构建。这使我们能够利用 LangGraph 的持久执行、人工干预支持、持久化等功能。

### 使用 LangSmith 进行调试
通过可视化工具深入了解复杂的智能体行为，跟踪执行路径，捕获状态转换，并提供详细的运行时指标。

## 安装
```bash
pip install -U langchain
```

## 创建智能体示例
```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# 运行智能体
agent.invoke({
    "messages": [{"role": "user", "content": "what is the weather in sf"}]
})
```

## 推荐使用场景
- 想要快速构建智能体和自主应用程序时使用 LangChain
- 当有更高级需求需要结合确定性和智能工作流、重度定制和精心控制的延迟时使用 LangGraph

LangChain 智能体基于 LangGraph 构建，以提供持久执行、流式传输、人工干预、持久化等功能。对于基本的 LangChain 智能体使用，您不需要了解 LangGraph。

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/overview