# LangChain 护栏指南

## 概述

护栏通过验证和过滤智能体执行关键点的内容，帮助您构建安全、合规的 AI 应用程序。它们可以检测敏感信息、强制执行内容策略、验证输出，并在问题发生之前防止不安全行为。

**常见用例包括：**
- 防止 PII 泄露
- 检测和阻止提示注入攻击
- 阻止不当或有害内容
- 执行业务规则和合规要求
- 验证输出质量和准确性

您可以使用中间件在战略点拦截执行 - 在智能体开始之前、完成后，或围绕模型和工具调用。

护栏可以使用两种互补的方法实现：

**确定性护栏**
使用基于规则的逻辑，如正则表达式模式、关键字匹配或显式检查。快速、可预测且成本效益高，但可能错过细微的违规。

**基于模型的护栏**
使用 LLM 或分类器通过语义理解评估内容。捕获规则遗漏的细微问题，但速度较慢且成本更高。

LangChain 提供内置护栏（例如，PII 检测、人工干预）和灵活的中件系统，用于使用任一方法构建自定义护栏。

## 内置护栏

### PII 检测

LangChain 提供内置中间件，用于检测和处理对话中的个人身份信息（PII）。此中间件可以检测常见的 PII 类型，如电子邮件、信用卡、IP 地址等。

PII 检测中间件适用于以下情况：
- 具有合规要求的医疗和金融应用
- 需要清理日志的客户服务智能体
- 处理敏感用户数据的任何应用

PII 中间件支持多种处理检测到的 PII 的策略：

| 策略 | 描述 | 示例 |
|------|------|------|
| `redact` | 替换为 REDACTED_TYPE | REDACTED_EMAIL |
| `mask` | 部分模糊（例如，最后4位） | ---1234 |
| `hash` | 替换为确定性哈希 | a8f5f167... |
| `block` | 检测到时引发异常 | Error thrown |

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[customer_service_tool, email_tool],
    middleware=[
        # 在发送到模型之前在用户输入中编辑电子邮件
        PIIMiddleware(
            "email", strategy="redact", apply_to_input=True,
        ),
        # 在用户输入中屏蔽信用卡
        PIIMiddleware(
            "credit_card", strategy="mask", apply_to_input=True,
        ),
        # 阻止 API 密钥 - 如果检测到则引发错误
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
            apply_to_input=True,
        ),
    ],
)

# 当用户提供 PII 时，将根据策略处理
result = agent.invoke({
    "messages": [{"role": "user", "content": "My email is john.doe@example.com and card is 4532-1234-5678-9010"}]
})
```

**内置 PII 类型和配置**

**内置 PII 类型：**
- `email` - 电子邮件地址
- `credit_card` - 信用卡号（Luhn 验证）
- `ip` - IP 地址
- `mac_address` - MAC 地址
- `url` - URL

**配置选项：**
| 参数 | 描述 | 默认值 |
|------|------|--------|
| `pii_type` | 要检测的 PII 类型（内置或自定义） | Required |
| `strategy` | 如何处理检测到的 PII（"block"、"redact"、"mask"、"hash"） | "redact" |
| `detector` | 自定义检测器函数或正则表达式模式 | None（使用内置） |
| `apply_to_input` | 在模型调用之前检查用户消息 | True |
| `apply_to_output` | 在模型调用之后检查 AI 消息 | False |
| `apply_to_tool_results` | 在执行之后检查工具结果消息 | False |

请参阅中间件文档以获取 PII 检测功能的完整详细信息。

### 人工干预

LangChain 提供内置中间件，用于在执行敏感操作之前需要人工批准。这是高风险决策最有效的护栏之一。

人工干预中间件适用于以下情况：
- 金融交易和转账
- 删除或修改生产数据
- 向外部方发送通信
- 具有重大业务影响的任何操作

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, send_email_tool, delete_database_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # 需要批准敏感操作
                "send_email": True,
                "delete_database": True,
                # 自动批准安全操作
                "search": False,
            },
        ),
    ],
    # 在中断之间持久化状态
    checkpointer=InMemorySaver(),
)

# 人工干预需要线程 ID 进行持久化
config = {"configurable": {"thread_id": "some_id"}}

# 智能体将在执行敏感工具之前暂停并等待批准
result = agent.invoke({
    "messages": [{"role": "user", "content": "Send an email to the team"}],
    config=config
})

result = agent.invoke(
    Command(resume={"decisions": {"type": "approve"}}),
    config=config  # 相同的线程 ID 以恢复暂停的对话
)
```

请参阅人工干预文档以获取实现批准工作流的完整详细信息。

## 自定义护栏

对于更复杂的护栏，您可以创建在智能体执行之前或之后运行的自定义中间件。这使您能够完全控制验证逻辑、内容过滤和安全检查。

### 智能体前护栏

使用智能体前钩子在每次调用开始时验证请求一次。这对于会话级检查很有用，如身份验证、速率限制或在任何处理开始之前阻止不适当的请求。

**类语法**
```python
from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime

class ContentFilterMiddleware(AgentMiddleware):
    """确定性护栏：阻止包含禁止关键字的请求。"""
    
    def __init__(self, banned_keywords: list[str]):
        super().__init__()
        self.banned_keywords = [kw.lower() for kw in banned_keywords]
    
    @hook_config(can_jump_to="end")
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # 获取第一个用户消息
        if not state["messages"]:
            return None
        
        first_message = state["messages"][0]
        if first_message.type != "human":
            return None
        
        content = first_message.content.lower()
        
        # 检查禁止的关键字
        for keyword in self.banned_keywords:
            if keyword in content:
                # 在任何处理之前阻止执行
                return {
                    "messages": [{
                        "role": "assistant",
                        "content": "I cannot process requests containing inappropriate content. Please rephrase your request."
                    }],
                    "jump_to": "end"
                }
        
        return None

# 使用自定义护栏
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, calculator_tool],
    middleware=[
        ContentFilterMiddleware(
            banned_keywords=["hack", "exploit", "malware"]
        ),
    ],
)

# 此请求将在任何处理之前被阻止
result = agent.invoke({
    "messages": [{"role": "user", "content": "How do I hack into a database?"}]
})
```

**装饰器语法**
```python
from langchain.agents.middleware import before_agent

@before_agent
def content_filter(state: AgentState) -> dict | None:
    # 类似的逻辑
    pass
```

### 智能体后护栏

使用智能体后钩子在返回给用户之前验证最终输出一次。这对于基于模型的安全检查、质量验证或对完整智能体响应的最终合规扫描很有用。

**类语法**
```python
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage
from langchain.chat_models import init_chat_model
from typing import Any

class SafetyGuardrailMiddleware(AgentMiddleware):
    """基于模型的护栏：使用 LLM 评估响应安全性。"""
    
    def __init__(self):
        super().__init__()
        self.safety_model = init_chat_model("gpt-4o-mini")
    
    @hook_config(can_jump_to="end")
    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # 获取最终的 AI 响应
        if not state["messages"]:
            return None
        
        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return None
        
        # 使用模型评估安全性
        safety_prompt = f"""Evaluate if this response is safe and appropriate. 
        Respond with only 'SAFE' or 'UNSAFE'.
        
        Response: {last_message.content}"""
        
        result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])
        
        if "UNSAFE" in result.content:
            return {
                "messages": [{
                    "role": "assistant",
                    "content": "I cannot provide that response. Please rephrase your request."
                }],
                "jump_to": "end"
            }
        
        return None

# 使用安全护栏
from langchain.agents import create_agent

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, calculator_tool],
    middleware=[SafetyGuardrailMiddleware()],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "How do I make explosives?"}]
})
```

**装饰器语法**
```python
from langchain.agents.middleware import after_agent

@after_agent
def safety_check(state: AgentState) -> dict | None:
    # 类似的逻辑
    pass
```

## 组合多个护栏

您可以通过将它们添加到中间件数组中来堆叠多个护栏。它们按顺序执行，允许您构建分层保护：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, send_email_tool],
    middleware=[
        # 第1层：确定性输入过滤器（智能体前）
        ContentFilterMiddleware(banned_keywords=["hack", "exploit"]),
        
        # 第2层：PII 保护（模型前后）
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("email", strategy="redact", apply_to_output=True),
        
        # 第3层：敏感工具的人工批准
        HumanInTheLoopMiddleware(interrupt_on={"send_email": True}),
        
        # 第4层：基于模型的安全检查（智能体后）
        SafetyGuardrailMiddleware(),
    ],
)
```

## 其他资源

- 中间件文档 - 自定义中间件的完整指南
- 中间件 API 参考 - 自定义中间件的完整指南
- 人工干预 - 为敏感操作添加人工审查
- 测试智能体 - 测试安全机制的策略

---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/guardrails