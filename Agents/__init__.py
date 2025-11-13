# 🐱 Agents模块包 - __init__.py
# 统一管理Agents模块的导入和初始化

"""
NekoAgent - Agents模块包

这个包包含了NekoAgent的所有核心组件：
- Agent核心类
- 模块化组件
- LLM模型接口
- 中间件系统
"""

import os
import sys

# 添加当前目录到Python路径，确保模块导入正常
_current_dir = os.path.dirname(__file__)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# 版本信息
__version__ = "1.0.0"
__author__ = "Neko Team"
__description__ = "NekoAgent - 月光中的流动存在"

# 核心类导出
from .Agent import Agent, get_studio_agent

# 模块化组件导出
from .Modular.CommandHandler import CommandHandler, create_command_handler
from .Modular.ThreadManager import ThreadManager, create_thread_manager
from .Modular.InteractiveMenus import InteractiveMenus, create_interactive_menus
from .Modular.HelpManager import HelpManager, create_help_manager

# 工具函数导出
from .Agent import list_available_roles, get_system_prompt, get_default_prompt

# 模块初始化函数
def initialize_agents():
    """
    初始化Agents模块
    
    Returns:
        dict: 初始化状态信息
    """
    from .Modular._setup import setup_logging
    
    # 设置日志
    setup_logging()
    
    # 设置环境变量
    os.environ["OLLAMA_GPU_LAYERS"] = "100"
    os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
    os.environ["OLLAMA_KEEP_ALIVE"] = "0"
    
    return {
        "status": "success",
        "message": "Agents模块初始化完成",
        "version": __version__,
        "available_components": {
            "Agent": "核心Agent类",
            "CommandHandler": "命令处理器",
            "ThreadManager": "线程管理器",
            "InteractiveMenus": "交互式菜单",
            "HelpManager": "帮助管理器"
        }
    }

# 模块信息函数
def get_module_info():
    """
    获取模块信息
    
    Returns:
        dict: 模块信息
    """
    return {
        "name": "Agents",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "Agent": "核心Agent类，负责对话和工具调用",
            "CommandHandler": "处理用户命令和斜杠命令",
            "ThreadManager": "管理对话线程和状态",
            "InteractiveMenus": "提供交互式选择菜单",
            "HelpManager": "统一的帮助信息管理"
        }
    }

# 可用性检查
def check_availability():
    """
    检查模块组件的可用性
    
    Returns:
        dict: 可用性状态
    """
    components = {
        "Agent": True,
        "CommandHandler": True,
        "ThreadManager": True,
        "InteractiveMenus": True,
        "HelpManager": True
    }
    
    # 检查每个组件
    try:
        from .Agent import Agent
        components["Agent"] = True
    except ImportError:
        components["Agent"] = False
    
    try:
        from .Modular.CommandHandler import CommandHandler
        components["CommandHandler"] = True
    except ImportError:
        components["CommandHandler"] = False
    
    try:
        from .Modular.ThreadManager import ThreadManager
        components["ThreadManager"] = True
    except ImportError:
        components["ThreadManager"] = False
    
    try:
        from .Modular.InteractiveMenus import InteractiveMenus
        components["InteractiveMenus"] = True
    except ImportError:
        components["InteractiveMenus"] = False
    
    try:
        from .Modular.HelpManager import HelpManager
        components["HelpManager"] = True
    except ImportError:
        components["HelpManager"] = False
    
    return {
        "status": "success" if all(components.values()) else "warning",
        "components": components,
        "message": "所有组件可用" if all(components.values()) else "部分组件不可用"
    }

# 快捷创建函数
def create_agent(checkpointer=None, model_type="deepseek", role_name="Neko", user_id="0"):
    """
    快捷创建Agent实例
    
    Args:
        checkpointer: 检查点类型
        model_type: 模型类型
        role_name: 角色名称
        user_id: 用户ID
        
    Returns:
        Agent实例
    """
    return Agent(
        checkpointer=checkpointer,
        model_type=model_type,
        role_name=role_name,
        user_id=user_id
    )

# 模块启动时的初始化
print(f"🐱 NekoAgent Agents模块 v{__version__} 已加载")

# 导出列表
__all__ = [
    # 核心类
    "Agent",
    "get_studio_agent",
    
    # 模块化组件
    "CommandHandler",
    "ThreadManager", 
    "InteractiveMenus",
    "HelpManager",
    
    # 创建函数
    "create_command_handler",
    "create_thread_manager", 
    "create_interactive_menus",
    "create_help_manager",
    "create_agent",
    
    # 工具函数
    "list_available_roles",
    "get_system_prompt", 
    "get_default_prompt",
    
    # 初始化函数
    "initialize_agents",
    "get_module_info",
    "check_availability"
]