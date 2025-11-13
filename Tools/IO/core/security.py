"""
统一安全检查模块

提供三层权限架构的安全检查：
1. 项目层 - 大保险箱（只读）
2. 沙盒层 - 游乐场（读写）  
3. 保险箱层 - 小保险箱（只进不出，只读不改）
"""

import os
from pathlib import Path
from .config import config


class SecurityManager:
    """统一安全管理器"""
    
    def validate_project_path(self, file_path: str) -> str:
        """
        验证项目范围路径
        
        Args:
            file_path: 相对或绝对路径
            
        Returns:
            绝对路径或None（如果不在项目范围内）
        """
        try:
            if not file_path or file_path.strip() == "":
                return None

            normalized_path = os.path.normpath(file_path)

            if os.path.isabs(normalized_path):
                abs_path = os.path.abspath(normalized_path)
            else:
                # 相对于项目根目录
                abs_path = os.path.abspath(os.path.join(config.PROJECT_ROOT, normalized_path))

            # 确保路径在项目范围内
            project_abs = os.path.abspath(config.PROJECT_ROOT)
            if not os.path.commonpath([abs_path, project_abs]) == project_abs:
                return None

            return abs_path

        except (ValueError, Exception):
            return None
    
    def validate_sandbox_path(self, file_path: str) -> str:
        """
        验证沙盒范围路径
        
        Args:
            file_path: 相对或绝对路径
            
        Returns:
            绝对路径或None（如果不在沙盒范围内）
        """
        try:
            # 规范化路径，处理 '..' 和 '.' 等
            normalized_path = os.path.normpath(file_path)

            # 解析路径
            if os.path.isabs(normalized_path):
                # 如果是绝对路径，检查是否在沙盒内
                abs_path = os.path.abspath(normalized_path)
            else:
                # 如果是相对路径，转换为沙盒内的绝对路径
                abs_path = os.path.abspath(os.path.join(config.SANDBOX_PATH, normalized_path))

            # 确保路径在沙盒内（使用规范化后的路径比较）
            sandbox_abs = os.path.abspath(config.SANDBOX_PATH)
            if not abs_path.startswith(sandbox_abs):
                return None

            return abs_path

        except Exception:
            return None
    
    def is_sensitive_path(self, file_path: str) -> bool:
        """
        检查是否为敏感路径
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为敏感路径
        """
        file_path_str = str(file_path).lower()
        
        sensitive_patterns = config.get_sensitive_patterns()
        return any(pattern in file_path_str for pattern in sensitive_patterns)
    
    def is_path_allowed(self, path: str) -> bool:
        """
        检查路径是否在允许访问的范围内
        
        Args:
            path: 路径
            
        Returns:
            是否允许访问
        """
        abs_path = os.path.abspath(path)

        # 检查路径是否以任何允许的基础路径开头
        for allowed_path in config.get_allowed_base_paths():
            allowed_abs = os.path.abspath(allowed_path)
            try:
                # 使用 Path 对象进行更安全的路径比较
                if Path(abs_path).is_relative_to(Path(allowed_abs)):
                    return True
            except ValueError:
                # 路径不相关，继续检查下一个
                continue

        return False
    
    def safebox_check(self, operation: str, file_path: str) -> tuple:
        """
        保险箱操作检查：只进不出，只读不改
        
        Args:
            operation: 操作类型 (READ, WRITE, DELETE, MOVE)
            file_path: 文件路径
            
        Returns:
            (success, message)
        """
        # 检查是否在保险箱内
        safebox_abs = os.path.abspath(config.SAFEBOX_PATH)
        if not file_path.startswith(safebox_abs):
            return True, ""  # 非保险箱操作
        
        # 保险箱保护规则
        if operation == "READ":
            return True, "允许读取保险箱内容"
        
        elif operation == "WRITE":
            # 只允许创建新文件，不允许覆盖
            if not os.path.exists(file_path):
                return True, "允许在保险箱内添加新文件"
            else:
                return False, "保险箱内不允许修改现有文件"
        
        else:  # DELETE, MOVE等
            return False, f"保险箱内禁止{operation}操作"
    
    def is_safe_file_type(self, file_path: str) -> bool:
        """
        检查文件类型是否安全可读
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为安全文件类型
        """
        safe_extensions = config.get_safe_file_extensions()

        # 限制文件大小（例如最大2MB）
        try:
            if os.path.getsize(file_path) > 2 * 1024 * 1024:  # 2MB
                return False
        except OSError:
            return False

        _, ext = os.path.splitext(file_path)
        return ext.lower() in safe_extensions or os.path.basename(file_path).lower() in safe_extensions


# 创建全局安全管理器实例
security = SecurityManager()