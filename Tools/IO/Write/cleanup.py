"""
统一基准的清理工具

使用项目根目录作为路径基准，与读取工具保持一致
"""

from langchain.tools import tool
import os
from Tools.IO.core import security, utils
from Tools.IO.core.config import config


def _cleanup_empty_directories_impl(target_path: str = ".", recursive: bool = True, dry_run: bool = False, description: str = "") -> tuple:
    """
    统一基准的清理空目录实现函数

    Args:
        target_path (str): 相对于项目根目录的目标路径，默认当前目录
        recursive (bool): 是否递归清理子目录，默认True
        dry_run (bool): 预览模式，不实际删除，默认False
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    try:
        # 安全检查1：确保目标路径在项目范围内
        abs_target_path = security.validate_project_path(target_path)
        if not abs_target_path:
            return False, f"错误：目标路径 '{target_path}' 不在项目范围内"

        # 安全检查2：确保目标路径在沙盒内
        sandbox_abs = os.path.abspath(config.SANDBOX_PATH)
        if not abs_target_path.startswith(sandbox_abs):
            return False, f"错误：目标路径 '{target_path}' 不在沙盒目录内"

        # 安全检查3：检查路径是否存在
        if not os.path.exists(abs_target_path):
            return False, f"错误：路径 '{target_path}' 不存在"

        # 安全检查4：确保是目录
        if not os.path.isdir(abs_target_path):
            return False, f"错误：路径 '{target_path}' 不是目录"

        # 安全检查5：保险箱保护检查
        safebox_check = security.safebox_check("CLEANUP", abs_target_path)
        if not safebox_check[0]:
            return False, f"错误：{safebox_check[1]}"

        # 安全检查6：防止清理系统关键目录
        if security.is_sensitive_path(abs_target_path):
            return False, f"错误：不允许清理系统关键目录 '{os.path.basename(abs_target_path)}'"

        def find_empty_directories(root_path: str, current_recursive: bool) -> list:
            """递归查找空目录"""
            empty_dirs = []
            
            try:
                for item in os.listdir(root_path):
                    item_path = os.path.join(root_path, item)
                    
                    # 跳过敏感路径
                    if security.is_sensitive_path(item_path):
                        continue
                    
                    # 跳过隐藏文件和目录
                    if item.startswith('.'):
                        continue
                    
                    if os.path.isdir(item_path):
                        # 递归查找子目录
                        if current_recursive:
                            empty_dirs.extend(find_empty_directories(item_path, current_recursive))
                        
                        # 检查当前目录是否为空
                        if utils.is_directory_empty(item_path):
                            empty_dirs.append(item_path)
            except PermissionError:
                # 没有权限访问的目录，跳过
                pass
                
            return empty_dirs

        # 查找空目录
        empty_dirs = find_empty_directories(abs_target_path, recursive)
        
        if not empty_dirs:
            return True, f"在路径 '{target_path}' 中未找到空目录"

        # 预览模式
        if dry_run:
            dir_list = "\n".join([f"  - {os.path.relpath(dir_path, sandbox_abs)}" for dir_path in empty_dirs])
            return True, f"预览模式 - 将删除以下空目录：\n{dir_list}\n\n总计：{len(empty_dirs)} 个空目录"

        # 实际删除操作
        deleted_count = 0
        deleted_dirs = []
        
        for dir_path in empty_dirs:
            try:
                # 再次检查是否为空（防止并发修改）
                if utils.is_directory_empty(dir_path):
                    # 创建备份信息
                    backup_path = utils.create_directory_backup_info(dir_path, f"清理前备份: {description}")
                    
                    # 删除空目录
                    os.rmdir(dir_path)
                    deleted_count += 1
                    deleted_dirs.append(f"  - {os.path.relpath(dir_path, sandbox_abs)} (备份: {backup_path})")
            except Exception as e:
                # 单个目录删除失败不影响其他目录
                continue

        if deleted_count == 0:
            return True, f"在路径 '{target_path}' 中未找到可删除的空目录"

        deleted_list = "\n".join(deleted_dirs)
        success_message = f"已成功删除 {deleted_count} 个空目录：\n{deleted_list}"

        # 记录操作日志
        utils.log_operation("CLEANUP", abs_target_path, description, deleted_count)

        return True, success_message

    except Exception as e:
        return False, f"清理空目录时发生错误：{e}"


@tool
def cleanup_empty_directories(target_path: str = ".", recursive: bool = True, dry_run: bool = False, description: str = "") -> tuple:
    """
    【权限说明】统一基准的沙盒空目录清理工具

    🐱 猫猫权限：只能在沙盒内清理空目录，但使用项目根目录基准

    ✅ 允许操作：
    - 在 Sandbox 内清理空目录
    - 递归清理子目录中的空目录
    - 预览模式（不实际删除）

    ❌ 禁止操作：
    - 不能删除非空目录
    - 不能删除系统关键目录
    - 不能删除沙盒外的目录
    - 不能删除包含文件的目录
    - 保险箱目录受到保护

    📝 正确示例：
    - cleanup_empty_directories()                    ← 清理整个猫窝的空目录
    - cleanup_empty_directories("Sandbox/test_area")        ← 清理特定区域
    - cleanup_empty_directories(dry_run=True)       ← 预览模式
    - cleanup_empty_directories(recursive=False)    ← 只清理当前目录

    🚫 错误示例：
    - cleanup_empty_directories("Agents/")          ← 试图清理项目目录
    - cleanup_empty_directories("/tmp/")            ← 沙盒外目录禁止
    - cleanup_empty_directories("Sandbox/_backups/")        ← 系统目录禁止
    - cleanup_empty_directories("Sandbox/Neko_SafeBox/")    ← 保险箱目录禁止

    Args:
        target_path (str): 相对于项目根目录的目标路径，默认当前目录
        recursive (bool): 是否递归清理子目录，默认True
        dry_run (bool): 预览模式，不实际删除，默认False
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    return _cleanup_empty_directories_impl(target_path, recursive, dry_run, description)


@tool
def cleanup_playground(description: str = "Neko猫窝日常整理") -> tuple:
    """
    【快捷工具】统一基准的猫窝整理工具

    🐱 猫猫权限：一键整理整个猫窝，使用项目根目录基准

    ✅ 功能：
    - 递归清理整个沙盒的空目录
    - 自动跳过受保护的系统目录
    - 绝对保护Neko保险箱及其内容
    - 创建操作备份和日志

    📝 使用示例：
    - cleanup_playground()                    ← 日常整理
    - cleanup_playground("测试后清理")        ← 带描述整理

    Args:
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    return _cleanup_empty_directories_impl("Sandbox", True, False, description)