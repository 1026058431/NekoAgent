"""
统一基准的删除文件工具

使用项目根目录作为路径基准，与读取工具保持一致
"""

from langchain.tools import tool
import os
from Tools.IO.core import security, utils
from Tools.IO.core.config import config


def _delete_file_impl(file_path: str, description: str = "") -> tuple:
    """
    统一基准的删除文件实现函数

    Args:
        file_path (str): 相对于项目根目录的文件路径
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    try:
        # 安全检查1：确保目标路径在项目范围内
        abs_file_path = security.validate_project_path(file_path)
        if not abs_file_path:
            return False, f"错误：文件路径 '{file_path}' 不在项目范围内"

        # 安全检查2：确保目标路径在沙盒内
        sandbox_abs = os.path.abspath(config.SANDBOX_PATH)
        if not abs_file_path.startswith(sandbox_abs):
            return False, f"错误：文件路径 '{file_path}' 不在沙盒目录内"

        # 安全检查3：检查路径是否存在
        if not os.path.exists(abs_file_path):
            return False, f"错误：路径 '{file_path}' 不存在"

        # 安全检查4：保险箱保护检查
        safebox_check = security.safebox_check("DELETE", abs_file_path)
        if not safebox_check[0]:
            return False, f"错误：{safebox_check[1]}"

        # 安全检查5：防止删除系统关键文件
        if security.is_sensitive_path(abs_file_path):
            return False, f"错误：不允许删除系统关键路径 '{os.path.basename(abs_file_path)}'"

        # 安全检查6：防止删除备份和日志文件
        backup_log_patterns = ['_backups/', '_logs/', '.backup_', '.meta']
        file_path_str = str(abs_file_path)
        if any(pattern in file_path_str for pattern in backup_log_patterns):
            return False, f"错误：不允许删除备份或日志文件 '{os.path.basename(abs_file_path)}'"

        # 创建备份（总是创建备份，确保安全）
        if os.path.isfile(abs_file_path):
            backup_path = utils.create_backup(abs_file_path, f"删除前备份: {description}")
            backup_info = f"文件已备份至: {backup_path}"
        else:
            backup_path = utils.create_directory_backup_info(abs_file_path, f"删除前备份: {description}")
            backup_info = f"目录信息已备份至: {backup_path}"

        # 执行删除操作
        if os.path.isfile(abs_file_path):
            os.remove(abs_file_path)
            success_message = f"文件已成功删除：{file_path}\n{backup_info}"
        else:
            # 检查目录是否为空
            if not utils.is_directory_empty(abs_file_path):
                return False, f"错误：目录 '{file_path}' 不为空，无法删除"
            os.rmdir(abs_file_path)
            success_message = f"空目录已成功删除：{file_path}\n{backup_info}"

        # 记录操作日志
        utils.log_operation("DELETE", file_path, description, 0)

        return True, success_message

    except PermissionError:
        return False, f"没有权限删除路径：{file_path}"
    except Exception as e:
        return False, f"删除路径时发生错误：{e}"


@tool
def delete_file(file_path: str, description: str = "") -> tuple:
    """
    【权限说明】统一基准的沙盒路径删除工具

    🐱 猫猫权限：只能在沙盒内删除文件或空目录（自动备份），但使用项目根目录基准

    ✅ 允许操作：
    - 在 Sandbox 内删除文件
    - 在 Sandbox 内删除空目录
    - 删除子目录中的文件

    ❌ 禁止操作：
    - 不能删除项目核心文件
    - 不能删除沙盒外的文件
    - 不能删除非空目录
    - 不能删除系统关键文件
    - 不能删除备份和日志文件
    - 保险箱内禁止删除操作

    📝 正确示例：
    - delete_file("Sandbox/test.txt")                    ← 删除根目录文件
    - delete_file("Sandbox/subdir/test.txt")            ← 删除子目录文件
    - delete_file("Sandbox/empty_dir")                  ← 删除空目录

    🚫 错误示例：
    - delete_file("Agents/test.py")             ← 试图删除项目文件
    - delete_file("/tmp/test.txt")              ← 沙盒外文件禁止
    - delete_file("Sandbox/_backups/test.txt")          ← 备份文件禁止删除
    - delete_file("Sandbox/non_empty_dir")              ← 非空目录禁止删除
    - delete_file("Sandbox/Neko_SafeBox/file")          ← 保险箱内禁止删除

    Args:
        file_path (str): 相对于项目根目录的文件路径
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    return _delete_file_impl(file_path, description)