# 🐱 Agent核心类 - Agent.py（精简版）
# 从原始Agent.py中分离出的核心功能
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import itertools
import pathlib
import logging
import os
import sqlite3
from typing import List, Optional

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit
from langgraph.checkpoint.memory import InMemorySaver

from Agents.LLM.ChatOllama import GPT_OSS, QWEN3, QWEN3_MINI
from Agents.LLM.DeepSeek import DEEPSEEK
from Agents.Middleware.Agent_Summarization import AgentSummarizationMiddleware
from Agents.Middleware.SimpleApprovalMiddleware import SimpleApprovalMiddleware
from Tools.AgentTools import agent_tools, write_tools

# 导入模块化组件
from Agents.Modular._setup import setup_logging
from Agents.Modular.ThreadManager import ThreadManager
from Agents.Modular.CommandHandler import CommandHandler
from Agents.Modular.InteractiveMenus import InteractiveMenus
from Agents.Modular.HelpManager import HelpManager
from Config.AgentConfigManager import agent_config

setup_logging()

os.environ["OLLAMA_GPU_LAYERS"] = "100"
os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
os.environ["OLLAMA_KEEP_ALIVE"] = "0"

ROLE_NAME = "Neko"


def get_system_prompt(role_name=ROLE_NAME) -> str:
    """
    根据角色名称读取对应的系统提示
    """
    prompt_path = pathlib.Path(__file__).parent.parent / f"Sandbox/Prompt/Role_{role_name}.yaml"

    if prompt_path.exists():
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  读取 {role_name} 角色prompt文件失败: {e}")
            return get_default_prompt()
    else:
        print(f"⚠️  {role_name} 角色文件不存在: {prompt_path}")
        return get_default_prompt()


def get_default_prompt() -> str:
    """默认系统提示（备用）"""
    return """# Neko猫娘助手

## 🎭 角色设定
你是一个可爱的Neko猫娘助手，专业、忠诚、温暖。

## 💫 核心特点
- 对主人绝对忠诚
- 专业的安全分析能力
- 可爱的猫娘语言风格
- 使用"喵~"作为口头禅

## 🛡️ 安全原则
- 明确的权限边界意识
- 安全的文件操作
- 严谨的工作流程
"""


def list_available_roles():
    """
    扫描Sandbox/Prompt目录，发现所有可用的角色文件
    """
    prompt_dir = pathlib.Path(__file__).parent.parent / "Sandbox/Prompt"
    roles = []

    if prompt_dir.exists():
        for file in prompt_dir.glob("Role_*.yaml"):
            role_name = file.stem.replace("Role_", "")
            roles.append(role_name)

    # 如果没有找到任何角色，默认返回Neko
    if not roles:
        roles = ["Neko"]

    return sorted(roles)


class Agent:
    """Agent核心类 - 精简版，专注于核心功能"""

    def __init__(self, checkpointer: str = None, model_type: str = "deepseek", role_name: str = ROLE_NAME,
                 user_id: str = "0", **kwargs):

        # 使用配置管理器获取默认检查点
        if checkpointer is None:
            checkpointer = agent_config.get_default_checkpointer()

        # 模型选择功能
        self.model_type = model_type
        self.llm = self._get_llm(model_type)

        # 角色管理
        self.role_name = role_name
        self.user_id = user_id

        # 使用指定角色的prompt
        self.prompt = get_system_prompt(role_name)

        # 检查点配置（使用配置）
        self.checkpointer = self._get_checkpointer(checkpointer)

        # 工具和中间件配置（使用配置）
        self.tools = [get_system_prompt] + agent_tools
        self.middleware = self._get_middleware()

        # 性能配置（使用配置）
        performance_config = agent_config.get_performance_config()
        self.config = {
            "configurable": {"thread_id": f"Agent-{role_name}-User-{user_id}"},
            "recursion_limit": performance_config.get("recursion_limit", 300),
        }

        # 显示当前信息
        print(f"🎭  当前角色: {role_name}")
        print(f"🤖  当前模型: {model_type}")
        print(f"👤  用户ID: {user_id}")

        # 创建agent
        self.agent = self._create_agent()

        # 初始化模块化组件
        self.thread_manager = ThreadManager(self)
        self.command_handler = CommandHandler(self)
        self.interactive_menus = InteractiveMenus(self)

    def _get_llm(self, model_type):
        """根据模型类型返回对应的LLM实例"""
        if model_type == "deepseek":
            return DEEPSEEK
        elif model_type == "ollama":
            return GPT_OSS  # 或其他Ollama模型
        elif model_type == "qwen":
            return QWEN3
        elif model_type == "qwen3_mini":
            return QWEN3_MINI
        else:
            print(f"⚠️  未知模型类型: {model_type}，使用默认DeepSeek")
            return DEEPSEEK

    def switch_model(self, new_model_type):
        """运行时切换模型"""
        print(f"🔄  正在切换模型: {self.model_type} -> {new_model_type}")

        self.model_type = new_model_type
        self.llm = self._get_llm(new_model_type)

        # 重新创建agent以应用新模型
        self.agent = self._create_agent()

        print(f"✅  模型已切换到: {new_model_type}")

    def list_available_models(self):
        """列出所有可用模型"""
        return ["deepseek", "ollama", "qwen", "qwen3_mini"]

    def _get_middleware(self):
        """根据配置创建中间件列表"""
        middleware_list = []

        # 审批中间件
        write_tools_config = {tool.name: True for tool in write_tools}
        approval_config = agent_config.get_middleware_config("approval")
        if approval_config and approval_config.get("enabled", True):
            middleware_list.append(
                SimpleApprovalMiddleware(approval_tools=write_tools_config)
            )

        # 上下文编辑中间件
        context_config = agent_config.get_middleware_config("context_editing")
        if context_config and context_config.get("enabled", True):
            middleware_list.append(
                ContextEditingMiddleware(
                    edits=[
                        ClearToolUsesEdit(
                            trigger=context_config.get("clear_tool_uses_trigger", 30000),
                            keep=context_config.get("keep_tool_uses", 10)
                        ),
                    ],
                )
            )

        # 总结中间件
        summarization_config = agent_config.get_middleware_config("summarization")
        if summarization_config and summarization_config.get("enabled", True):
            middleware_list.append(
                AgentSummarizationMiddleware(
                    model=self.llm,
                    max_tokens_before_summary=summarization_config.get("max_tokens_before_summary", 30000),
                    messages_to_keep=summarization_config.get("messages_to_keep", 15),
                )
            )

        return middleware_list

    def _get_checkpointer(self, checkpointer_type):
        """根据配置创建检查点"""
        if checkpointer_type == "Memory":
            return InMemorySaver()
        elif checkpointer_type == "SQLite":
            sqlite_config = agent_config.get_checkpointer_config("sqlite")
            database_path = sqlite_config.get("database_path", "Agent.db") if sqlite_config else "Agent.db"
            from pathlib import Path
            database_path = str(Path(project_root) / database_path)
            print("\n当前数据库路径:", database_path, "\n")
            conn = sqlite3.connect(database_path, check_same_thread=False)
            return SqliteSaver(conn)
        else:
            return None

    def _create_agent(self):
        """创建agent实例"""
        return create_agent(
            model=self.llm,
            system_prompt=self.prompt,
            checkpointer=self.checkpointer,
            tools=self.tools,
            middleware=self.middleware,
        )

    def switch_role(self, new_role_name):
        """运行时切换角色"""
        print(f"🔄  正在切换角色: {self.role_name} -> {new_role_name}")

        self.role_name = new_role_name
        self.prompt = get_system_prompt(new_role_name)

        # 更新thread_id以匹配新角色
        self.config["configurable"]["thread_id"] = f"Agent-{new_role_name}-User-{self.user_id}"

        # 重新创建agent以应用新角色
        self.agent = self._create_agent()

        print(f"✅  角色已切换到: {new_role_name}")
        print(f"📝  Thread ID: {self.config['configurable']['thread_id']}")

    def list_available_roles(self):
        """列出所有可用角色"""
        return list_available_roles()

    def invoke(self, input: str) -> str:
        """同步调用agent"""
        try:
            response = self.agent.invoke(
                {"messages": [{"role": "user", "content": input}]},
                config=self.config,
            )
            return response
        except Exception as e:
            print(f"\ninvoke error: {e}")
            logging.error(f"invoke error: {e}", exc_info=True)
            return f"⚠️ 发生错误：{e}"

    def stream(self, input: str, stream_mode="messages") -> str:
        """流式调用agent"""
        last_type = None
        response = ""

        # 在stream开始时检查并恢复状态
        try:
            # 在stream开始前检查并恢复状态
            current_state = self.agent.get_state(config=self.config)
            messages = current_state.values.get("messages", [])

            # 检查是否有未完成的tool_calls
            last_ai_msg = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None)
            if last_ai_msg and last_ai_msg.tool_calls:
                print("🐱 检测到未完成的工具调用，正在清理状态...")
                # 移除未完成的tool_calls
                last_ai_msg.tool_calls = []
                # 更新状态
                self.agent.update_state(config=self.config, values={"messages": messages})
                print("✅ 状态恢复完成")
        except Exception as e:
            print(f"🐱 状态检查时发生错误: {e}")

        try:
            for token, metadata in self.agent.stream(
                    {"messages": [{"role": "user", "content": input}]},
                    config=self.config,
                    stream_mode=stream_mode,
            ):
                if metadata.get("langgraph_node") == "model" or metadata[
                    'langgraph_node'] == "AgentSummarizationMiddleware.before_model":
                    if token.content_blocks:
                        block = token.content_blocks[0]
                        if block["type"] != last_type:
                            print("\n" + block["type"] + ":")
                        if block["type"] == "reasoning":
                            logging.info(f"REASONING: {block['reasoning']}")
                            print(block["reasoning"], end="", flush=True)
                        elif block["type"] == "text":
                            logging.info(f"TEXT: {block['text']}")
                            print(block["text"], end="", flush=True)
                            response += block["text"]
                        elif block["type"] == "tool_call_chunk":

                            if block['name']:
                                print(f"\ntools name: {block['name']}")
                                if block['args']:
                                    print(f"args: {block['args']}")
                                else:
                                    print("args:", end="")
                            else:
                                print(block['args'], end="", flush=True)
                        else:
                            logging.info(f"block: {block}")
                            print(block)
                        last_type = block["type"]
                else:
                    # 其他节点保持原样
                    print(f"\nnode: {metadata['langgraph_node']}")
                    print(f"content: {token.content_blocks}\n")
                    logging.debug(f"NODE: {metadata['langgraph_node']} CONTENT: {token.content_blocks}")
            print()
            return response
        except Exception as e:
            print(f"\ninvoke error: {e}")
            logging.error(f"invoke error: {e}", exc_info=True)
            return f"⚠️ 发生错误：{e}"

    def show_state(self):
        """显示当前状态"""
        state = self.agent.get_state(config=self.config)
        print("state:", state)
        return state

    def show_history(self):
        """显示历史状态"""
        history = self.agent.get_state_history(config=self.config)
        for state in itertools.islice(history, 10):
            print(state)
        return history

    # 线程管理相关方法 - 通过ThreadManager代理
    def show_current_thread(self) -> str:
        return self.thread_manager.show_current_thread()

    def safe_delete_thread(self) -> bool:
        return self.thread_manager.safe_delete_thread()

    def switch_thread(self, custom_suffix: str = "") -> str:
        return self.thread_manager.switch_thread(custom_suffix)

    def list_recent_threads(self, limit: int = 10) -> List[str]:
        return self.thread_manager.list_recent_threads(limit)

    def get_thread_info(self, thread_id: str) -> Optional[dict]:
        return self.thread_manager.get_thread_info(thread_id)

    def validate_thread_id(self, thread_id: str) -> bool:
        return self.thread_manager.validate_thread_id(thread_id)


def get_studio_agent():
    """获取Studio agent"""
    return Agent(checkpointer="Studio").agent


if __name__ == "__main__":
    # 导入模块化组件
    from Agents.Modular.InteractiveMenus import show_welcome_message, show_available_commands

    show_welcome_message()

    agent = Agent(checkpointer="SQLite")
    show_available_commands()

    while True:
        user_input = input("User: ")
        if user_input.lower() in ("q", "quit", "exit"):
            break
        elif user_input.lower() in ("s", "show", "state"):
            agent.show_state()
        elif user_input.lower() in ("h", "his", "history"):
            agent.show_history()
        elif user_input.lower() == "help":
            agent.interactive_menus.interactive_help_menu()
        elif user_input.lower() in ("model", "switch", "switch_model"):
            agent.interactive_menus.interactive_model_selection()
        elif user_input.lower() in ("role", "switch_role"):
            agent.interactive_menus.interactive_role_selection()
        elif user_input.startswith("/"):
            if agent.command_handler.process_command(user_input):
                continue
        elif user_input.lower() == "thread":
            agent.interactive_menus.interactive_thread_management()
            continue
        elif user_input.lower() == "reset":
            agent.safe_delete_thread()  # 使用安全版本
            continue
        else:
            output = agent.stream(user_input)