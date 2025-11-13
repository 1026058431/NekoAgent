"""
通用工具函数模块

提供IO工具的通用功能：备份、日志等
"""

import os
import shutil
import uuid
from datetime import datetime
from .config import config
from .security import security


class IOUtils:
    """IO通用工具类"""
    
    def create_backup(self, original_path: str, description: str = "") -> str:
        """
        创建文件备份
        
        Args:
            original_path: 原始文件路径
            description: 备份描述
            
        Returns:
            备份文件路径
        """
        # 确保备份目录存在
        if not os.path.exists(config.BACKUP_DIR):
            os.makedirs(config.BACKUP_DIR, exist_ok=True)

        # 生成带时间戳的备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(original_path)
        backup_name = f"{file_name}.backup_{timestamp}_{uuid.uuid4().hex[:8]}"

        backup_path = os.path.join(config.BACKUP_DIR, backup_name)

        # 复制文件内容
        with open(original_path, 'r', encoding='utf-8') as src:
            content = src.read()

        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)

        # 记录备份信息
        backup_info = f"Backup: {timestamp} - {description}" if description else f"Backup: {timestamp}"
        with open(backup_path + ".meta", 'w') as meta:
            meta.write(backup_info)

        return backup_path
    
    def create_directory_backup_info(self, dir_path: str, description: str = "") -> str:
        """
        创建目录备份信息（记录目录结构）
        
        Args:
            dir_path: 目录路径
            description: 备份描述
            
        Returns:
            备份信息文件路径
        """
        # 确保备份目录存在
        if not os.path.exists(config.BACKUP_DIR):
            os.makedirs(config.BACKUP_DIR, exist_ok=True)

        # 生成带时间戳的备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = os.path.basename(dir_path)
        backup_name = f"dir_{dir_name}.backup_{timestamp}_{uuid.uuid4().hex[:8]}.info"

        backup_path = os.path.join(config.BACKUP_DIR, backup_name)

        # 记录目录信息
        dir_info = f"Directory: {dir_path}\n"
        dir_info += f"Backup Time: {timestamp}\n"
        dir_info += f"Description: {description}\n"
        dir_info += f"Relative Path: {os.path.relpath(dir_path, config.SANDBOX_PATH)}\n"

        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(dir_info)

        return backup_path
    
    def log_operation(self, operation: str, file_path: str, description: str = "", content_length: int = 0) -> None:
        """
        记录操作日志
        
        Args:
            operation: 操作类型
            file_path: 文件路径
            description: 操作描述
            content_length: 内容长度
        """
        # 确保日志目录存在
        if not os.path.exists(config.LOGS_DIR):
            os.makedirs(config.LOGS_DIR, exist_ok=True)

        log_file = os.path.join(config.LOGS_DIR, "file_operations.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"{timestamp} | {operation} | {file_path} | {content_length} chars | {description}\n"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def ensure_directory_exists(self, dir_path: str) -> None:
        """
        确保目录存在
        
        Args:
            dir_path: 目录路径
        """
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    def is_directory_empty(self, dir_path: str) -> bool:
        """
        检查目录是否为空
        
        Args:
            dir_path: 目录路径
            
        Returns:
            目录是否为空
        """
        try:
            # 使用 listdir 检查目录内容
            items = os.listdir(dir_path)
            return len(items) == 0
        except (PermissionError, FileNotFoundError):
            return False
    
    def find_empty_directories(self, start_path: str, recursive: bool = True) -> list:
        """
        递归查找空目录
        
        Args:
            start_path: 起始路径
            recursive: 是否递归
            
        Returns:
            空目录列表
        """
        empty_dirs = []

        def _scan_directory(current_path: str):
            # 跳过敏感目录
            if security.is_sensitive_path(current_path):
                return

            # 检查当前目录是否为空
            if self.is_directory_empty(current_path):
                empty_dirs.append(current_path)
            
            # 如果递归扫描，继续检查子目录
            if recursive:
                try:
                    for item in os.listdir(current_path):
                        item_path = os.path.join(current_path, item)
                        if os.path.isdir(item_path) and not security.is_sensitive_path(item_path):
                            _scan_directory(item_path)
                except PermissionError:
                    pass  # 跳过无权限访问的目录

        _scan_directory(start_path)
        return empty_dirs


# 创建全局工具实例
utils = IOUtils()