# 🐱 命令处理模块 - CommandHandler.py
# 从Agent.py中分离的命令处理功能

from typing import List, Optional


class CommandHandler:
    """命令处理类 - 负责解析和处理用户命令"""
    
    def __init__(self, agent_instance):
        """
        初始化命令处理器
        
        Args:
            agent_instance: Agent实例，用于执行命令
        """
        self.agent = agent_instance
    
    def handle_thread_command(self, command_parts: List[str]) -> bool:
        """
        处理线程管理命令
        
        Args:
            command_parts: 命令分割后的列表
            
        Returns:
            是否处理了命令
        """
        if not command_parts:
            return False

        base_command = command_parts[0].lower()

        if base_command == "thread":
            if len(command_parts) == 1:
                # /thread - 显示当前线程
                print(f"\n{self.agent.show_current_thread()}")
                return True

            elif len(command_parts) >= 2:
                sub_command = command_parts[1].lower()

                if sub_command == "switch":
                    # /thread switch [自定义名]
                    if len(command_parts) >= 3:
                        custom_name = command_parts[2]
                        self.agent.switch_thread(custom_name)
                    else:
                        # /thread switch - 切换到默认线程
                        self.agent.switch_thread("")
                    return True

                elif sub_command == "list":
                    # /thread list - 显示线程列表
                    threads = self.agent.list_recent_threads(limit=10)
                    if threads:
                        print("\n📊 最近活跃线程:")
                        for i, thread_id in enumerate(threads, 1):
                            thread_info = self.agent.get_thread_info(thread_id)
                            if thread_info:
                                suffix_info = f" - {thread_info['custom_suffix']}" if thread_info['custom_suffix'] else ""
                                current_indicator = " 🔹" if thread_id == self.agent.config["configurable"]["thread_id"] else ""
                                print(f"  {i}. {thread_id}{suffix_info}{current_indicator}")
                            else:
                                current_indicator = " 🔹" if thread_id == self.agent.config["configurable"]["thread_id"] else ""
                                print(f"  {i}. {thread_id}{current_indicator}")
                    else:
                        print("❌ 没有找到活跃线程")
                    return True

                elif sub_command == "reset":
                    # /thread reset - 安全重置
                    self.agent.safe_delete_thread()
                    return True

                elif sub_command == "help":
                    # /thread help - 显示帮助
                    from Agents.Modular.HelpManager import create_help_manager
                    help_manager = create_help_manager(self.agent)
                    print(f"\n{help_manager.get_category_help('thread')}")
                    return True

        return False
    
    def parse_command(self, user_input: str) -> Optional[List[str]]:
        """
        解析用户输入的命令
        
        Args:
            user_input: 用户输入
            
        Returns:
            命令分割后的列表，如果不是命令则返回None
        """
        if user_input.startswith("/"):
            return user_input[1:].split()
        return None
    
    def process_command(self, user_input: str) -> bool:
        """
        处理用户命令
        
        Args:
            user_input: 用户输入
            
        Returns:
            是否处理了命令
        """
        command_parts = self.parse_command(user_input)
        if command_parts:
            return self.handle_thread_command(command_parts)
        return False


# 命令处理相关的工具函数
def create_command_handler(agent_instance):
    """
    创建命令处理器实例
    
    Args:
        agent_instance: Agent实例
        
    Returns:
        CommandHandler实例
    """
    return CommandHandler(agent_instance)


def get_thread_help_text():
    """返回线程管理命令的帮助文本"""
    from Agents.Modular.HelpManager import create_help_manager
    help_manager = create_help_manager()
    return help_manager.get_category_help("thread")


def get_full_help_text():
    """返回完整的帮助文本"""
    from Agents.Modular.HelpManager import create_help_manager
    help_manager = create_help_manager()
    return help_manager.get_full_help()