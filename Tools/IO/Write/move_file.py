"""
统一基准的移动文件工具

使用项目根目录作为路径基准，与读取工具保持一致
"""

from langchain.tools import tool
import os
import shutil
from Tools.IO.core import security, utils
from Tools.IO.core.config import config


def _move_file_impl(source_path: str, target_path: str, description: str = "") -> tuple:
    """
    统一基准的移动文件实现函数

    Args:
        source_path (str): 相对于项目根目录的源路径
        target_path (str): 相对于项目根目录的目标路径
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    try:
        # 安全检查1：确保源路径在项目范围内
        abs_source_path = security.validate_project_path(source_path)
        if not abs_source_path:
            return False, f"错误：源路径 '{source_path}' 不在项目范围内"

        # 安全检查2：确保目标路径在项目范围内
        abs_target_path = security.validate_project_path(target_path)
        if not abs_target_path:
            return False, f"错误：目标路径 '{target_path}' 不在项目范围内"

        # 安全检查3：确保源路径在沙盒内
        sandbox_abs = os.path.abspath(config.SANDBOX_PATH)
        if not abs_source_path.startswith(sandbox_abs):
            return False, f"错误：源路径 '{source_path}' 不在沙盒目录内"

        # 安全检查4：确保目标路径在沙盒内
        if not abs_target_path.startswith(sandbox_abs):
            return False, f"错误：目标路径 '{target_path}' 不在沙盒目录内"

        # 安全检查5：检查源路径是否存在
        if not os.path.exists(abs_source_path):
            return False, f"错误：源路径 '{source_path}' 不存在"

        # 安全检查6：保险箱保护检查
        safebox_check = security.safebox_check("MOVE", abs_source_path)
        if not safebox_check[0]:
            return False, f"错误：{safebox_check[1]}"
        
        safebox_check_target = security.safebox_check("MOVE", abs_target_path)
        if not safebox_check_target[0]:
            return False, f"错误：{safebox_check_target[1]}"

        # 安全检查7：防止移动系统关键文件
        if security.is_sensitive_path(abs_source_path):
            return False, f"错误：不允许移动系统关键路径 '{os.path.basename(abs_source_path)}'"

        # 安全检查8：防止覆盖系统关键文件
        if os.path.exists(abs_target_path) and security.is_sensitive_path(abs_target_path):
            return False, f"错误：不允许覆盖系统关键路径 '{os.path.basename(abs_target_path)}'"

        # 创建备份（如果目标路径已存在）
        backup_info = ""
        if os.path.exists(abs_target_path):
            if os.path.isfile(abs_target_path):
                backup_path = utils.create_backup(abs_target_path, f"移动前备份: {description}")
                backup_info = f"\n原目标文件已备份至: {backup_path}"
            else:
                backup_path = utils.create_directory_backup_info(abs_target_path, f"移动前备份: {description}")
                backup_info = f"\n原目标目录信息已备份至: {backup_path}"

        # 确保目标目录存在
        target_dir = os.path.dirname(abs_target_path)
        if target_dir and not os.path.exists(target_dir):
            utils.ensure_directory_exists(target_dir)

        # 执行移动操作
        shutil.move(abs_source_path, abs_target_path)

        # 根据类型生成成功消息
        if os.path.isfile(abs_source_path):
            success_message = f"文件已成功移动：{source_path} → {target_path}{backup_info}"
        else:
            success_message = f"目录已成功移动：{source_path} → {target_path}{backup_info}"

        # 记录操作日志
        utils.log_operation("MOVE", f"{source_path} -> {target_path}", description, 0)

        return True, success_message

    except PermissionError:
        return False, f"没有权限移动路径：{source_path}"
    except Exception as e:
        return False, f"移动路径时发生错误：{e}"


@tool
def move_file(source_path: str, target_path: str, description: str = "") -> tuple:
    """
    【权限说明】统一基准的沙盒路径移动工具

    🐱 猫猫权限：只能在沙盒内移动文件或目录，但使用项目根目录基准

    ✅ 允许操作：
    - 在 Sandbox 内移动文件
    - 在 Sandbox 内移动目录
    - 跨子目录移动文件或目录
    - 重命名文件或目录

    ❌ 禁止操作：
    - 不能移动项目核心文件
    - 不能移动沙盒外的文件
    - 不能移动系统关键文件
    - 不能覆盖系统关键文件
    - 保险箱内禁止移动操作

    📝 正确示例：
    - move_file("Sandbox/test.txt", "Sandbox/new_test.txt")           ← 重命名文件
    - move_file("Sandbox/test.txt", "Sandbox/subdir/test.txt")       ← 移动到子目录
    - move_file("Sandbox/subdir", "Sandbox/new_subdir")              ← 重命名目录
    - move_file("Sandbox/old_dir", "Sandbox/new_location/old_dir")   ← 移动目录

    🚫 错误示例：
    - move_file("Agents/test.py", "Sandbox/test.py")         ← 试图移动项目文件
    - move_file("/tmp/test.txt", "Sandbox/test.txt")         ← 沙盒外文件禁止
    - move_file("Sandbox/test.txt", "../test.txt")           ← 试图逃逸沙盒
    - move_file("Sandbox/Neko_SafeBox/file", "Sandbox/other") ← 保险箱内禁止移动

    Args:
        source_path (str): 相对于项目根目录的源文件路径
        target_path (str): 相对于项目根目录的目标文件路径
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    return _move_file_impl(source_path, target_path, description)