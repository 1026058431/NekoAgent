"""
统一配置管理模块

提供IO工具的统一配置，消除重复代码
"""

import os
from pathlib import Path


class IOConfig:
    """IO工具统一配置类"""
    
    def __init__(self):
        self._project_root = None
        self._sandbox_path = None
        self._backup_dir = None
        
    @property
    def PROJECT_ROOT(self) -> str:
        """项目根目录"""
        if self._project_root is None:
            self._project_root = self._get_project_root()
        return self._project_root
    
    @property
    def SANDBOX_PATH(self) -> str:
        """沙盒目录路径"""
        if self._sandbox_path is None:
            self._sandbox_path = self._get_sandbox_path()
        return self._sandbox_path
    
    @property
    def BACKUP_DIR(self) -> str:
        """备份目录路径"""
        if self._backup_dir is None:
            self._backup_dir = os.path.join(self.SANDBOX_PATH, "_backups")
        return self._backup_dir
    
    @property
    def LOGS_DIR(self) -> str:
        """日志目录路径"""
        return os.path.join(self.SANDBOX_PATH, "_logs")
    
    @property
    def SAFEBOX_DIR(self) -> str:
        """保险箱目录名"""
        return "SafeBox"
    
    @property
    def SAFEBOX_PATH(self) -> str:
        """保险箱完整路径"""
        return os.path.join(self.SANDBOX_PATH, self.SAFEBOX_DIR)
    
    def _get_project_root(self) -> str:
        """获取项目根目录"""
        # 优先从环境变量获取
        project_root = os.getenv("PROJECT_ROOT")
        if project_root:
            return str(project_root)
        
        # 推导项目根目录
        # 假设此文件在 Tools/IO/core/config.py
        current_file = Path(__file__)
        # Tools/IO/core/config.py -> Tools/IO/core -> Tools/IO -> Tools -> 项目根目录
        tools_dir = current_file.parent.parent.parent
        project_root = str(tools_dir.parent)
        
        return project_root
    
    def _get_sandbox_path(self) -> str:
        """获取沙盒目录路径"""
        # 优先从环境变量获取
        sandbox_path = os.getenv("SANDBOX_PATH")
        if sandbox_path:
            return str(sandbox_path)
        
        # 默认沙盒路径：项目根目录/Sandbox
        return str(Path(self.PROJECT_ROOT) / "Sandbox")
    
    def get_allowed_base_paths(self) -> list:
        """获取允许访问的基础路径列表"""
        return [
            self.SANDBOX_PATH,
            self.PROJECT_ROOT,
        ]
    
    def get_sensitive_patterns(self) -> list:
        """获取敏感文件模式列表"""
        return [
            # 配置和密钥文件
            '.env', '.env.', 'settings.', 'secrets.',
            'credentials', 'key', 'token', 'password', 'secret',
            # 版本控制
            '.git/', '.gitignore', '.gitattributes',
            # 系统和个人文件
            '/etc/', '/sys/', '/proc/', '.ssh/', '.aws/', '.npmrc',
            # 备份和日志
            '_backups', '_logs',
            # 证书和密钥文件
            '.pem', '.key', '.crt', '.pfx', '.p12', '.keystore',
            # IDE和编辑器配置
            '.idea/', '.vscode/', '.project', '.classpath',
            # 依赖管理
            'package-lock.json', 'yarn.lock', 'pipfile.lock'
            # 备份文件
            '_backups/', '_logs/'
        ]
    
    def get_safe_file_extensions(self) -> set:
        """获取安全的文件扩展名集合"""
        return {
            # 源代码文件
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs',
            '.php', '.rb', '.swift', '.kt', '.scala',
            # 标记和文档
            '.html', '.css', '.md', '.txt', '.rst', '.tex',
            # 数据文件
            '.json', '.yaml', '.yml', '.xml', '.csv', '.tsv',
            # 配置文件（非敏感）
            '.ini', '.conf', '.cfg',
            # 构建和项目文件
            '.dockerfile', 'dockerfile', '.gitignore', 'makefile', 'cmakelists.txt'
        }


# 创建全局配置实例
config = IOConfig()