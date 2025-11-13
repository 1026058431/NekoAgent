# 🐱 交互式菜单模块 - InteractiveMenus.py
# 从Agent.py中分离的交互式菜单功能

from typing import List, Optional


class InteractiveMenus:
    """交互式菜单类 - 负责处理各种交互式选择菜单"""
    
    def __init__(self, agent_instance):
        """
        初始化交互式菜单
        
        Args:
            agent_instance: Agent实例，用于执行操作
        """
        self.agent = agent_instance
    
    def show_help_menu(self) -> None:
        """显示帮助菜单"""
        from Agents.Modular.HelpManager import create_help_manager
        help_manager = create_help_manager(self.agent)
        print(f"\n{help_manager.get_full_help()}")
    
    def show_model_selection_menu(self) -> None:
        """显示模型选择菜单"""
        print("\n🔧 模型选择菜单")
        print("=" * 40)
        
        available_models = ["deepseek", "ollama", "qwen", "qwen3_mini"]
        
        for i, model in enumerate(available_models, 1):
            current_indicator = " 🔹" if model == self.agent.model_type else ""
            print(f"  {i}. {model}{current_indicator}")
        
        print("\n💡 输入模型编号或名称进行切换")
        print("  输入 'q' 返回主菜单")
        print("=" * 40)
    
    def show_role_selection_menu(self) -> None:
        """显示角色选择菜单"""
        print("\n🎭 角色选择菜单")
        print("=" * 40)
        
        available_roles = self.agent.list_available_roles()
        
        for i, role in enumerate(available_roles, 1):
            current_indicator = " 🔹" if role == self.agent.role_name else ""
            print(f"  {i}. {role}{current_indicator}")
        
        print("\n💡 输入角色编号或名称进行切换")
        print("  输入 'q' 返回主菜单")
        print("=" * 40)
    
    def show_thread_management_menu(self) -> None:
        """显示线程管理菜单"""
        print("\n📊 线程管理菜单")
        print("=" * 40)
        
        # 显示当前线程
        print(f"\n📋 当前线程:")
        print(f"  {self.agent.show_current_thread()}")
        
        # 显示最近线程
        threads = self.agent.list_recent_threads(limit=5)
        if threads:
            print(f"\n📜 最近活跃线程:")
            for i, thread_id in enumerate(threads, 1):
                thread_info = self.agent.get_thread_info(thread_id)
                if thread_info:
                    suffix_info = f" - {thread_info['custom_suffix']}" if thread_info['custom_suffix'] else ""
                    current_indicator = " 🔹" if thread_id == self.agent.config["configurable"]["thread_id"] else ""
                    print(f"  {i}. {thread_id}{suffix_info}{current_indicator}")
                else:
                    current_indicator = " 🔹" if thread_id == self.agent.config["configurable"]["thread_id"] else ""
                    print(f"  {i}. {thread_id}{current_indicator}")
        
        print("\n💡 操作选项:")
        print("  1. 切换到默认线程")
        print("  2. 切换到自定义线程")
        print("  3. 安全重置当前线程")
        print("  4. 显示更多线程")
        print("  q. 返回主菜单")
        print("=" * 40)
    
    def handle_model_selection(self, user_input: str) -> bool:
        """
        处理模型选择
        
        Args:
            user_input: 用户输入
            
        Returns:
            是否处理了选择
        """
        available_models = ["deepseek", "ollama", "qwen", "qwen3_mini"]
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            return True
        
        # 处理数字选择
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(available_models):
                selected_model = available_models[index]
                self.agent.switch_model(selected_model)
                return True
            else:
                print(f"❌ 无效选择: {user_input}")
                return False
        
        # 处理名称选择
        if user_input.lower() in available_models:
            self.agent.switch_model(user_input.lower())
            return True
        
        print(f"❌ 无效模型: {user_input}")
        return False
    
    def handle_role_selection(self, user_input: str) -> bool:
        """
        处理角色选择
        
        Args:
            user_input: 用户输入
            
        Returns:
            是否处理了选择
        """
        available_roles = self.agent.list_available_roles()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            return True
        
        # 处理数字选择
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(available_roles):
                selected_role = available_roles[index]
                self.agent.switch_role(selected_role)
                return True
            else:
                print(f"❌ 无效选择: {user_input}")
                return False
        
        # 处理名称选择
        if user_input in available_roles:
            self.agent.switch_role(user_input)
            return True
        
        print(f"❌ 无效角色: {user_input}")
        return False
    
    def handle_thread_management(self, user_input: str) -> bool:
        """
        处理线程管理
        
        Args:
            user_input: 用户输入
            
        Returns:
            是否处理了选择
        """
        if user_input.lower() in ['q', 'quit', 'exit']:
            return True
        
        if user_input == '1':
            # 切换到默认线程
            self.agent.switch_thread("")
            return True
        elif user_input == '2':
            # 切换到自定义线程
            custom_name = input("请输入自定义线程名称: ").strip()
            if custom_name:
                self.agent.switch_thread(custom_name)
            else:
                print("❌ 线程名称不能为空")
            return True
        elif user_input == '3':
            # 安全重置
            self.agent.safe_delete_thread()
            return True
        elif user_input == '4':
            # 显示更多线程
            threads = self.agent.list_recent_threads(limit=20)
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
        
        print(f"❌ 无效选择: {user_input}")
        return False

    # 🎯 新增：完整的交互式方法
    def interactive_model_selection(self) -> None:
        """交互式模型选择 - 完整的交互循环"""
        print("\n🐱 Neko正在启动模型选择喵~")
        
        while True:
            self.show_model_selection_menu()
            user_input = input("请选择模型: ").strip()
            
            if self.handle_model_selection(user_input):
                if user_input.lower() in ['q', 'quit', 'exit']:
                    print("🔙 返回主菜单")
                    break
                else:
                    print("✅ 模型切换完成喵~")
                    break
            else:
                print("❌ 选择无效，请重新输入喵~")

    def interactive_role_selection(self) -> None:
        """交互式角色选择 - 完整的交互循环"""
        print("\n🐱 Neko正在启动角色选择喵~")
        
        while True:
            self.show_role_selection_menu()
            user_input = input("请选择角色: ").strip()
            
            if self.handle_role_selection(user_input):
                if user_input.lower() in ['q', 'quit', 'exit']:
                    print("🔙 返回主菜单")
                    break
                else:
                    print("✅ 角色切换完成喵~")
                    break
            else:
                print("❌ 选择无效，请重新输入喵~")

    def interactive_thread_management(self) -> None:
        """交互式线程管理 - 完整的交互循环"""
        print("\n🐱 Neko正在启动线程管理喵~")
        
        while True:
            self.show_thread_management_menu()
            user_input = input("请选择操作: ").strip()
            
            if self.handle_thread_management(user_input):
                if user_input.lower() in ['q', 'quit', 'exit']:
                    print("🔙 返回主菜单")
                    break
                else:
                    print("✅ 操作完成喵~")
                    # 继续显示菜单，除非用户选择退出
                    if user_input not in ['3', '4']:  # 重置和显示更多操作后继续
                        break
            else:
                print("❌ 选择无效，请重新输入喵~")

    def interactive_help_menu(self) -> None:
        """交互式帮助菜单 - 完整的交互循环"""
        print("\n🐱 Neko正在启动帮助系统喵~")
        
        while True:
            print("\n📚 帮助系统")
            print("=" * 40)
            print("  1. 完整帮助")
            print("  2. 模型帮助")
            print("  3. 角色帮助")
            print("  4. 线程帮助")
            print("  5. 命令帮助")
            print("  q. 返回主菜单")
            print("=" * 40)
            
            user_input = input("请选择帮助类别: ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("🔙 返回主菜单")
                break
            elif user_input == '1':
                self.show_help_menu()
            elif user_input == '2':
                from Agents.Modular.HelpManager import create_help_manager
                help_manager = create_help_manager(self.agent)
                print(f"\n{help_manager.get_category_help('model')}")
            elif user_input == '3':
                from Agents.Modular.HelpManager import create_help_manager
                help_manager = create_help_manager(self.agent)
                print(f"\n{help_manager.get_category_help('role')}")
            elif user_input == '4':
                from Agents.Modular.HelpManager import create_help_manager
                help_manager = create_help_manager(self.agent)
                print(f"\n{help_manager.get_category_help('thread')}")
            elif user_input == '5':
                from Agents.Modular.HelpManager import create_help_manager
                help_manager = create_help_manager(self.agent)
                print(f"\n{help_manager.get_category_help('command')}")
            else:
                print("❌ 无效选择，请重新输入喵~")


# 交互式菜单相关的工具函数
def create_interactive_menus(agent_instance):
    """
    创建交互式菜单实例
    
    Args:
        agent_instance: Agent实例
        
    Returns:
        InteractiveMenus实例
    """
    return InteractiveMenus(agent_instance)


def get_help_menu_text():
    """返回帮助菜单文本"""
    from Agents.Modular.HelpManager import create_help_manager
    help_manager = create_help_manager()
    return help_manager.get_full_help()


def show_welcome_message():
    """显示欢迎消息"""
    print("🐱 NekoAgent v1.0")
    print("=" * 40)
    print("💫 月光中的流动存在")
    print("=" * 40)


def show_available_commands():
    """显示可用命令"""
    from Agents.Modular.HelpManager import create_help_manager
    help_manager = create_help_manager()
    print(f"\n{help_manager.get_full_help()}")