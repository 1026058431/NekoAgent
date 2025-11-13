"""
Neko简单审批中间件

🐱 功能：在工具调用前实时询问用户确认
📋 特点：简单实用，可配置需要审批的工具列表
"""

from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents.middleware.types import AgentMiddleware, AgentState
from langgraph.runtime import Runtime
from langgraph.types import Command

class SimpleApprovalMiddleware(AgentMiddleware):
    """简单审批中间件 - 使用after_model拦截"""

    def __init__(self, approval_tools=None):
        super().__init__()

        if approval_tools is None:
            approval_tools = {
                "write_file", "delete_file", "move_file",
                "cleanup_empty_directories", "cleanup_playground"
            }
        self.require_approval_tools = set(approval_tools)

    def after_model(self, state: AgentState, runtime: Runtime):
        """在模型生成响应后检查工具调用"""
        messages = state["messages"]
        if not messages:
            return None

        # 找到最后一个AI消息
        last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
        if not last_ai_msg or not last_ai_msg.tool_calls:
            return None

        # 检查是否有需要审批的工具
        tools_need_approval = []
        for tool_call in last_ai_msg.tool_calls:
            if tool_call["name"] in self.require_approval_tools:
                tools_need_approval.append(tool_call)

        if not tools_need_approval:
            return None

        # 对需要审批的工具询问用户
        approved_tool_calls = []  # 批准的工具
        user_feedback_messages = []  # 用户的反馈消息
        
        for tool_call in tools_need_approval:
            print(f"\n🐱 操作需要确认: {tool_call['name']}")
            print(f"参数: {tool_call['args']}")

            user_response = input("确认执行? (y/N): ").strip()

            if user_response.lower() in ['y', 'yes']:
                print("✅ 操作已批准")
                approved_tool_calls.append(tool_call)  # 保留批准的工具
            else:
                # 拒绝操作 - 创建用户反馈消息
                if user_response.lower() in ['n', 'no', '']:
                    user_feedback = "我拒绝了刚才的操作请求呢，你可以问问我拒绝的理由~"
                else:
                    user_feedback = f"我拒绝了刚才的操作请求呢，因为: {user_response}"

                print(f"❌ {user_feedback}")
                
                # 创建HumanMessage让对话继续
                user_feedback_messages.append(HumanMessage(content=user_feedback))
                # 注意：拒绝的工具不会添加到approved_tool_calls中

        # 构建新的tool_calls列表：
        # 1. 保留不需要审批的工具
        # 2. 保留批准的工具
        # 3. 移除拒绝的工具
        new_tool_calls = [
            tc for tc in last_ai_msg.tool_calls
            if tc not in tools_need_approval or tc in approved_tool_calls
        ]

        # 更新AI消息
        last_ai_msg.tool_calls = new_tool_calls

        # 如果有用户反馈消息，使用Command继续执行模型
        if user_feedback_messages:
            return Command(
                update={"messages": [last_ai_msg, *user_feedback_messages]},
                goto="model"  # 告诉系统继续执行模型
            )
        else:
            # 没有拒绝，正常返回
            return {"messages": [last_ai_msg]}