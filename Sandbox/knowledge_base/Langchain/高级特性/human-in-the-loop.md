# 人机交互

Human-in-the-Loop (HITL) 中间件让你可以向智能体工具调用添加人工监督。当模型提出可能需要审查的操作时——例如写入文件或执行SQL——中间件可以暂停执行并等待决策。它通过检查每个工具调用是否符合可配置的策略来实现这一点。

如果需要干预，中间件会发出一个中断，停止执行。图状态使用LangGraph的持久化层保存，因此执行可以安全地暂停并在稍后恢复。然后，人工决策确定接下来会发生什么：操作可以按原样批准（approve）、在运行前修改（edit）或拒绝并附带反馈（reject）。

## 中断决策类型

中间件定义了三种内置的人工响应中断的方式：

| 决策类型 | 描述 | 示例用例 |
|---------|------|----------|
| ✅ approve | 操作按原样批准并执行，不做更改 | 按原样发送电子邮件草稿 |
| ✏️ edit | 工具调用在修改后执行 | 在发送电子邮件前更改收件人 |
| ❌ reject | 工具调用被拒绝，并在对话中添加解释 | 拒绝电子邮件草稿并解释如何重写 |

每个工具的可用决策类型取决于你在 `interrupt_on` 中配置的策略。当多个工具调用同时暂停时，每个操作都需要单独的决策。决策必须按照操作在中断请求中出现的顺序提供。

在编辑工具参数时，要保守地进行更改。对原始参数的显著修改可能导致模型重新评估其方法，并可能多次执行工具或采取意外操作。

## 配置中断

要使用HITL，在创建智能体时将其添加到智能体的中间件列表中。你配置一个工具操作到每个操作允许的决策类型的映射。当工具调用匹配映射中的操作时，中间件将中断执行。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="gpt-4o",
    tools=[write_file_tool, execute_sql_tool, read_data_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": True,  # 允许所有决策（approve、edit、reject）
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},  # 不允许编辑
                # 安全操作，不需要批准
                "read_data": False,
            },
            # 中断消息的前缀 - 与工具名称和参数组合形成完整消息
            # 例如："Tool execution pending approval: execute_sql with query='DELETE FROM...'"
            # 单个工具可以通过在其中断配置中指定 "description" 来覆盖此设置
            description_prefix="Tool execution pending approval",
        ),
    ],
    # Human-in-the-loop需要检查点来处理中断。
    # 在生产环境中，使用持久化检查点如AsyncPostgresSaver。
    checkpointer=InMemorySaver(),
)
```

你必须配置一个检查点来在中断之间持久化图状态。在生产环境中，使用持久化检查点如 `AsyncPostgresSaver`。对于测试或原型设计，使用 `InMemorySaver`。

在调用智能体时，传递一个包含线程ID的配置，以将执行与会话线程关联。有关详细信息，请参阅LangGraph中断文档。

## 响应中断

当你调用智能体时，它会运行直到完成或引发中断。当工具调用匹配你在 `interrupt_on` 中配置的策略时，会触发中断。在这种情况下，调用结果将包含一个 `__interrupt__` 字段，其中包含需要审查的操作。

然后你可以将这些操作呈现给审查者，并在提供决策后恢复执行。

```python
from langgraph.types import Command

# Human-in-the-loop利用LangGraph的持久化层。
# 你必须提供一个线程ID来将执行与会话线程关联，
# 以便对话可以暂停和恢复（这是人工审查所需的）。
config = {"configurable": {"thread_id": "some_id"}}

# 运行图直到遇到中断。
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Delete old records from the database",
            }
        ]
    },
    config=config
)

# 中断包含完整的HITL请求，包含action_requests和review_configs
print(result['__interrupt__'])
# > [
# >   Interrupt(
# >     value={
# >       'action_requests': [
# >         {
# >           'name': 'execute_sql',
# >           'arguments': {'query': 'DELETE FROM records WHERE created_at < NOW() - INTERVAL \\'30 days\\';'},
# >           'description': 'Tool execution pending approval\\n\\nTool: execute_sql\\nArgs: {...}'
# >         }
# >       ],
# >       'review_configs': [
# >         {
# >           'action_name': 'execute_sql',
# >           'allowed_decisions': ['approve', 'reject']
# >         }
# >       ]
# >     }
# >   )
# > ]

# 使用批准决策恢复
agent.invoke(
    Command(
        resume={"decisions": [{"type": "approve"}]}  # 或 "edit", "reject"
    ),
    config=config  # 相同的线程ID以恢复暂停的对话
)
```

## 决策类型

### ✅ approve

使用 `approve` 按原样批准工具调用并执行，不做更改。

```python
agent.invoke(
    Command(
        # 决策作为列表提供，每个正在审查的操作一个。
        # 决策的顺序必须与 `__interrupt__` 请求中列出的操作顺序匹配。
        resume={
            "decisions": [
                {
                    "type": "approve",
                }
            ]
        }
    ),
    config=config  # 相同的线程ID以恢复暂停的对话
)
```

## 执行生命周期

中间件定义了一个 `after_model` 钩子，在模型生成响应后但在任何工具调用执行之前运行：

1. 智能体调用模型生成响应。
2. 中间件检查响应中的工具调用。
3. 如果任何调用需要人工输入，中间件构建一个包含 `action_requests` 和 `review_configs` 的HITLRequest并调用中断。
4. 智能体等待人工决策。
5. 基于HITLResponse决策，中间件执行已批准或已编辑的调用，为被拒绝的调用合成ToolMessage，并恢复执行。

## 自定义HITL逻辑

对于更专业的工作流，你可以直接使用中断原语和中间件抽象构建自定义HITL逻辑。查看上面的执行生命周期以了解如何将中断集成到智能体的操作中。---
**原始文档URL**: https://docs.langchain.com/oss/python/langchain/human-in-the-loop