"""
IO工具核心模块

提供统一的配置、安全和工具函数
"""

from .config import IOConfig
from .security import SecurityManager
from .utils import IOUtils

# 创建全局实例
config = IOConfig()
security = SecurityManager()
utils = IOUtils()

__all__ = ["config", "security", "utils", "IOConfig", "SecurityManager", "IOUtils"]