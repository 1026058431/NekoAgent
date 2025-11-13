"""
统一基准的读取文件工具

使用项目根目录作为路径基准，与写入工具保持一致
"""

import os
from langchain.tools import tool
from Tools.IO.core import security, utils


def _read_file_impl(file_path: str, encoding: str = "utf-8") -> tuple:
    """
    统一基准的读取文件实现函数 - 项目范围

    Args:
        file_path (str): 相对于项目根目录的相对文件路径
        encoding (str, optional): 文件编码

    Returns:
        tuple: (success, content_or_message)
    """
    try:
        # 安全检查1：确保目标路径在项目范围内
        abs_file_path = security.validate_project_path(file_path)
        if not abs_file_path:
            return False, f"错误：文件路径 '{file_path}' 不在项目范围内"

        # 安全检查2：敏感文件检查
        if security.is_sensitive_path(abs_file_path):
            return False, f"错误：不允许读取敏感文件 '{os.path.basename(abs_file_path)}'"

        if not os.path.exists(abs_file_path):
            return False, f"文件不存在：{abs_file_path}"

        # 安全检查3：文件类型和大小安全检查
        if not security.is_safe_file_type(abs_file_path):
            return False, f"错误：文件类型可能不安全或文件过大"

        with open(abs_file_path, 'r', encoding=encoding) as f:
            content = f.read()

        # 记录操作日志
        utils.log_operation("READ", abs_file_path, "", len(content))
        return True, content

    except Exception as e:
        return False, f"读文件时发生错误：{e}"


@tool
def read_file(file_path: str, encoding: str = "utf-8") -> tuple:
    """
    【权限说明】统一基准的只读访问工具

    🐱 猫猫权限：可以看，不能改（项目范围，统一基准）

    ✅ 允许操作：
    - 读取 Sandbox 内的文件："Sandbox/文件名"
    - 读取项目其他文件：相对路径（相对于项目根目录）

    ❌ 禁止操作：
    - 不能修改任何文件内容
    - 不能读取系统敏感文件
    - 不能越权访问项目范围外的文件

    📝 正确示例：
    - read_file("Sandbox/test.py")     ← 读取沙盒文件
    - read_file("Agents/prompt.yaml")  ← 读取项目文件

    🚫 错误示例：
    - read_file("test.py")             ← 缺少路径前缀
    - read_file("/etc/passwd")         ← 系统文件禁止访问

    Args:
        file_path (str): 相对于项目根目录的相对文件路径
        encoding (str, optional): 文件编码

    Returns:
        tuple: (success, content_or_message)
    """
    return _read_file_impl(file_path, encoding)