# 🐱 Agents.Modular 模块化组件包
# 这是Agent.py的模块化分离版本

"""
Agents.Modular 模块化组件包

这个包包含了Agent.py的模块化分离版本：
- ThreadManager: 线程管理模块
- CommandHandler: 命令处理模块  
- InteractiveMenus: 交互式菜单模块

使用说明：
1. 导入方式：from Agents.Modular import ThreadManager, CommandHandler, InteractiveMenus
2. 或者：from Agents.Modular.ThreadManager import ThreadManager
3. 主要用于Agent.py内部使用

注意：这个包是Agent.py的内部组件，不建议直接从外部导入使用。
"""

__version__ = "1.0.0"
__author__ = "Neko"

# 定义包的公开接口
__all__ = [
    "ThreadManager",
    "CommandHandler", 
    "InteractiveMenus",
    "create_thread_manager",
    "create_command_handler", 
    "create_interactive_menus",
    "show_welcome_message",
    "show_available_commands",
    "get_thread_help_text",
    "get_full_help_text"
]

# 导入主要类，方便直接使用 from Agents.Modular import ThreadManager
from .ThreadManager import ThreadManager, create_thread_manager
from .CommandHandler import CommandHandler, create_command_handler, get_thread_help_text, get_full_help_text
from .InteractiveMenus import InteractiveMenus, create_interactive_menus, show_welcome_message, show_available_commands

# 包级别初始化（可选）
print("🐱 Agents.Modular 模块化组件包已加载")