"""
统一路径基准的IO工具模块

修正认知偏差：所有IO工具都使用项目根目录作为路径基准

三层权限架构保持不变：
1. 项目层 - 大保险箱（只读）
2. 沙盒层 - 游乐场（读写）  
3. 保险箱层 - 小保险箱（只进不出，只读不改）
"""

from .Read import read_file, list_dir_tree, get_current_path, get_current_time
from .Write import write_file, move_file, delete_file, cleanup_empty_directories, cleanup_playground

__all__ = [
    # 读取工具（项目范围，统一基准）
    "read_file",
    "list_dir_tree",
    "get_current_path", 
    "get_current_time",
    
    # 写入工具（沙盒范围，统一基准）
    "write_file",
    "move_file",
    "delete_file",
    "cleanup_empty_directories",
    "cleanup_playground",
]