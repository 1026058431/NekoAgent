# 多智能体

多智能体系统将复杂的应用程序分解为多个专门的智能体，这些智能体协同工作来解决问题。与其依赖单个智能体处理每个步骤，多智能体架构允许你将更小、更专注的智能体组合成协调的工作流。

多智能体系统在以下情况下很有用：
- 单个智能体有太多工具，并且在决定使用哪个工具时做出糟糕的决策
- 上下文或内存增长太大，单个智能体无法有效跟踪
- 任务需要专业化（例如，规划者、研究员、数学专家）

## 多智能体模式

| 模式 | 工作原理 | 控制流 | 示例用例 |
|------|----------|--------|----------|
| **Tool Calling** | 监督智能体将其他智能体作为工具调用。"工具"智能体不直接与用户交谈——它们只是运行任务并返回结果。 | 集中式：所有路由都通过调用智能体 | 任务编排、结构化工作流 |
| **Handoffs** | 当前智能体决定将控制权转移给另一个智能体。活动智能体发生变化，用户可能继续直接与新智能体交互。 | 分散式：智能体可以改变谁处于活动状态 | 多领域对话、专家接管 |

**教程：构建监督智能体**

学习如何使用监督模式构建个人助手，其中中央监督智能体协调专门的工人智能体。本教程演示：
- 为不同领域（日历和电子邮件）创建专门的子智能体
- 将子智能体包装为工具以进行集中编排
- 为敏感操作添加人工审查

[了解更多](https://docs.langchain.com/oss/python/langchain/tutorials/supervisor-agent)

## 选择模式

| 问题 | Tool Calling | Handoffs |
|------|-------------|----------|
| 需要对工作流进行集中控制？ | ✅ 是 | ❌ 否 |
| 希望智能体直接与用户交互？ | ❌ 否 | ✅ 是 |
| 专家之间复杂的类人对话？ | ❌ 有限 | ✅ 强 |

你可以混合使用两种模式——使用handoffs进行智能体切换，并让每个智能体将子智能体作为工具调用以执行专门任务。

## 自定义智能体上下文

多智能体设计的核心是上下文工程——决定每个智能体看到什么信息。LangChain让你可以细粒度地控制：
- 对话或状态的哪些部分传递给每个智能体
- 为子智能体定制的专门提示
- 中间推理的包含/排除
- 每个智能体的自定义输入/输出格式

你的系统质量在很大程度上取决于上下文工程。目标是确保每个智能体都能访问执行其任务所需的正确数据，无论是作为工具还是作为活动智能体。

## 工具调用

在工具调用中，一个智能体（"控制器"）将其他智能体视为在需要时调用的工具。控制器管理编排，而工具智能体执行特定任务并返回结果。

流程：
1. 控制器接收输入并决定调用哪个工具（子智能体）
2. 工具智能体基于控制器的指令运行其任务
3. 工具智能体将结果返回给控制器
4. 控制器决定下一步或完成

用作工具的智能体通常不期望继续与用户对话。它们的角色是执行任务并将结果返回给控制器智能体。如果你需要子智能体能够与用户对话，请改用handoffs。

## 实现

下面是一个最小示例，其中主智能体通过工具定义获得对单个子智能体的访问权限：

```python
from langchain.tools import tool
from langchain.agents import create_agent

subagent1 = create_agent(model="...", tools=[...])

@tool(
    "subagent1_name",
    description="subagent1_description"
)
def call_subagent1(query: str):
    result = subagent1.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    return result["messages"][-1].content

agent = create_agent(model="...", tools=[call_subagent1])
```

在这种模式中：
- 当主智能体决定任务匹配子智能体的描述时，它会调用 `call_subagent1`
- 子智能体独立运行并返回其结果
- 主智能体接收结果并继续编排

## 自定义点

有几个点可以控制上下文在主智能体及其子智能体之间传递的方式：

- **子智能体名称（"subagent1_name"）**：这是主智能体引用子智能体的方式。由于它影响提示，请仔细选择。
- **子智能体描述（"subagent1_description"）**：这是主智能体"知道"的关于子智能体的信息。它直接塑造主智能体决定何时调用它。
- **输入到子智能体**：你可以自定义此输入以更好地塑造子智能体解释任务的方式。在上面的示例中，我们直接传递智能体生成的查询。
- **从子智能体输出**：这是传递回主智能体的响应。你可以调整返回的内容以控制主智能体解释结果的方式。在上面的示例中，我们返回最终消息文本，但你可以返回额外的状态或元数据。

## 控制输入到子智能体

有两个主要杠杆可以控制主智能体传递给子智能体的输入：

- **修改提示** - 调整主智能体的提示或工具元数据（即子智能体的名称和描述）以更好地指导它何时以及如何调用子智能体。
- **上下文注入** - 通过调整工具调用以从智能体状态中提取，添加无法在静态提示中捕获的输入（例如，完整的消息历史、先前的结果、任务元数据）。

```python
from langchain.agents import AgentState
from langchain.tools import tool, ToolRuntime

class CustomState(AgentState):
    example_state_key: str

@tool(
    "subagent1_name",
    description="subagent1_description"
)
def call_subagent1(query: str, runtime: ToolRuntime[None, CustomState]):
    # 应用任何需要的逻辑将消息转换为合适的输入
    subagent_input = some_logic(query, runtime.state["messages"])
    
    result = subagent1.invoke({
        "messages": subagent_input,
        # 你也可以在这里根据需要传递其他状态键。
        # 确保在主智能体和子智能体的状态模式中都定义这些。
        "example_state_key": runtime.state["example_state_key"]
    })
    
    return result["messages"][-1].content
```

## 控制从子智能体输出

塑造主智能体从子智能体接收的内容的两种常见策略：

- **修改提示** - 优化子智能体的提示以确切指定应返回什么。当输出不完整、过于冗长或缺少关键细节时很有用。一个常见的失败模式是子智能体执行工具调用或推理但未在其最终消息中包含结果。提醒它控制器（和用户）只看到最终输出，因此所有相关信息必须包含在那里。
- **自定义输出格式化** - 在将子智能体的响应交还给主智能体之前，在代码中调整或丰富它。

示例：将特定的状态键传递回主智能体，除了最终文本。这需要将结果包装在Command（或等效结构）中，以便你可以将自定义状态与子智能体的响应合并。

```python
from typing import Annotated
from langchain.agents import AgentState
from langchain.tools import InjectedToolCallId
from langgraph.types import Command

@tool(
    "subagent1_name",
    description="subagent1_description"
)
# 我们需要将 `tool_call_id` 传递给子智能体，以便它可以使用它来响应工具调用结果
def call_subagent1(
    query: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    # 你需要返回一个 `Command` 对象以包含不仅仅是最终工具调用
) -> Command:
    result = subagent1.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    
    return Command(update={
        # 这是我们传递回的示例状态键
        "example_state_key": result["example_state_key"],
        "messages": [
            ToolMessage(
                content=result["messages"][-1].content,
                # 我们需要包含工具调用ID，以便它与正确的工具调用匹配
                tool_call_id=tool_call_id
            )
        ]
    })
```

## Handoffs

在handoffs中，智能体可以直接将控制权传递给彼此。"活动"智能体发生变化，用户与当前拥有控制权的任何智能体交互。

流程：
1. 当前智能体决定需要另一个智能体的帮助
2. 它将控制权（和状态）传递给下一个智能体
3. 新智能体直接与用户交互，直到它决定再次handoff或完成

## 实现（即将推出）---

**原始文档URL**: https://docs.langchain.com/oss/python/langchain/multi-agent