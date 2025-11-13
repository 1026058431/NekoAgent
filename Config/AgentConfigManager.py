"""
🐱 Agent专用配置管理器

核心功能：
- 管理中间件、检查点、性能配置
- 支持配置热重载
- 提供默认配置回退
"""

import os
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("neko.agent_config")


class AgentConfigManager:
    """Agent专用配置管理器"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_config()
    
    def _get_config_path(self) -> str:
        """获取配置文件路径（相对于项目根目录）"""
        # 获取当前文件所在目录（Config文件夹）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 获取项目根目录（Config文件夹的父目录的父目录）
        project_root = os.path.dirname(current_dir)
        # 构建相对于项目根目录的配置文件路径
        config_path = os.path.join(project_root, "Config", "agent_config.yaml")
        return config_path
    
    def _load_config(self) -> Dict[str, Any]:
        """加载Agent配置"""
        config_path = self._get_config_path()
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    logger.info(f"Agent配置加载成功: {config_path}")
                    return config.get("agent", {})
            else:
                logger.warning(f"Agent配置文件不存在: {config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"加载Agent配置失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "middleware": {
                "summarization": {
                    "enabled": True,
                    "max_tokens_before_summary": 30000,
                    "messages_to_keep": 15
                },
                "context_editing": {
                    "enabled": True,
                    "clear_tool_uses_trigger": 30000,
                    "keep_tool_uses": 10
                },
                "approval": {
                    "enabled": True
                }
            },
            "checkpointer": {
                "default": "SQLite",
                "sqlite": {
                    "database_path": "Agent.db",
                    "check_same_thread": False
                },
                "memory": {
                    "enabled": True
                }
            },
            "performance": {
                "recursion_limit": 30,
                "stream_mode": "messages",
                "state_recovery": True
            }
        }
    
    def get_middleware_config(self, middleware_type: str) -> Optional[Dict[str, Any]]:
        """获取中间件配置"""
        middleware = self._config.get("middleware", {})
        return middleware.get(middleware_type)
    
    def get_checkpointer_config(self, checkpointer_type: str) -> Optional[Dict[str, Any]]:
        """获取检查点配置"""
        checkpointer = self._config.get("checkpointer", {})
        return checkpointer.get(checkpointer_type)
    
    def get_default_checkpointer(self) -> str:
        """获取默认检查点类型"""
        return self._config.get("checkpointer", {}).get("default", "SQLite")
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return self._config.get("performance", {})
    
    def reload(self) -> bool:
        """重新加载配置"""
        try:
            self._config = self._load_config()
            logger.info("Agent配置重新加载成功")
            return True
        except Exception as e:
            logger.error(f"Agent配置重新加载失败: {e}")
            return False


# 全局配置管理器实例
agent_config = AgentConfigManager()