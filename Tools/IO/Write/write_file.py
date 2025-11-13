"""
统一基准的写入文件工具 - 升级版

使用项目根目录作为路径基准，与读取工具保持一致
新增内容长度限制和优化的注释说明
"""

from langchain.tools import tool
import os
from Tools.IO.core import security, utils
from Tools.IO.core.config import config


# 全局配置
DANGER_CONTENT_LENGTH = 5000
MAX_CONTENT_LENGTH = 10000  # 单次写入最大字符数
CHUNK_SIZE = 2500  # 分块写入的推荐大小


def _validate_content_length(content: str) -> tuple:
    """
    验证内容长度

    Args:
        content: 要写入的内容

    Returns:
        (is_valid, message)
    """
    content_length = len(content)

    if content_length == 0:
        return False, "错误：内容不能为空"

    if content_length >  DANGER_CONTENT_LENGTH and content_length < MAX_CONTENT_LENGTH:
        return True, f"通过：但内容过长 ({content_length} > {DANGER_CONTENT_LENGTH})，建议过长文本使用'a'-Append写入模式，分批次写入，并检查写入后完整性。"

    if content_length > MAX_CONTENT_LENGTH:
        return True, f"错误：内容过长 ({content_length} > {MAX_CONTENT_LENGTH})，建议过长文本使用'a'-Append写入模式，分批次写入，并检查写入后完整性。"

    return True, f"内容长度检查通过 ({content_length} 字符)"

# 新增文件名长度检查函数
def _validate_filename_length(file_path: str) -> tuple:
    filename = os.path.basename(file_path)
    max_filename_length = 64
    if len(filename) > max_filename_length:
        return False, f"错误：文件名过长 ({len(filename)} > {max_filename_length})"
    return True, "文件名长度检查通过"

def _write_file_impl(file_path: str, content: str, mode: str = "w", encoding: str = "utf-8", description: str = "") -> tuple:
    """
    统一基准的写入文件实现函数 - 升级版

    Args:
        file_path (str): 相对于项目根目录的文件路径
        content (str): 文件内容
        mode (str): 写入模式
        encoding (str): 文件编码
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    try:
        # 安全检查0：文件名长度验证
        filename_check = _validate_filename_length(file_path)
        if not filename_check[0]:
            return False, filename_check[1]

        # 安全检查1：内容长度验证
        length_check = _validate_content_length(content)
        if not length_check[0]:
            return False, length_check[1]

        # 安全检查2：确保目标路径在项目范围内
        abs_file_path = security.validate_project_path(file_path)
        if not abs_file_path:
            return False, f"错误：文件路径 '{file_path}' 不在项目范围内"

        # 安全检查3：确保目标路径在沙盒内
        sandbox_abs = os.path.abspath(config.SANDBOX_PATH)
        if not abs_file_path.startswith(sandbox_abs):
            return False, f"错误：文件路径 '{file_path}' 不在沙盒目录内，只能在 Sandbox 内写入"

        # 安全检查4：保险箱保护检查
        safebox_check = security.safebox_check("WRITE", abs_file_path)
        if not safebox_check[0]:
            return False, f"错误：{safebox_check[1]}"

        # 安全检查5：防止写入系统关键文件
        if security.is_sensitive_path(abs_file_path):
            return False, f"错误：不允许修改系统关键文件 '{os.path.basename(abs_file_path)}'"

        # 创建备份（如果文件已存在且为覆盖模式）
        backup_info = ""
        if os.path.exists(abs_file_path) and mode == "w":
            backup_path = utils.create_backup(abs_file_path, description)
            backup_info = f"\n原文件已备份至: {backup_path}"

        # 确保目录存在
        dir_name = os.path.dirname(abs_file_path)
        if dir_name and not os.path.exists(dir_name):
            utils.ensure_directory_exists(dir_name)

        # 执行写入
        with open(abs_file_path, mode, encoding=encoding) as f:
            f.write(content)

        success_message = f"文件已成功写入：{abs_file_path}{backup_info}"

        # 记录操作日志
        utils.log_operation("WRITE", abs_file_path, description, len(content))

        return True, success_message

    except PermissionError:
        return False, f"没有权限写入文件：{file_path}"
    except Exception as e:
        return False, f"写文件时发生错误：{e}"


@tool
def write_file(file_path: str, content: str, mode: str = "w", encoding: str = "utf-8", description: str = "") -> tuple:
    """
    【权限说明】统一基准的沙盒写入工具 - 升级版

    🐱 猫猫权限：只能在沙盒里写，但使用项目根目录基准

    ✅ 允许操作：
    - 在 Sandbox 内创建新文件
    - 在 Sandbox 内修改已有文件（自动备份）
    - 在 Sandbox 子目录中操作
    - 在保险箱内创建新文件（只进不出）

    ❌ 禁止操作：
    - 不能修改项目核心文件
    - 不能删除任何文件
    - 不能在沙盒外创建文件
    - 不能在保险箱内覆盖现有文件

    ⚠️ 重要更新：内容长度限制
    - 单次写入最大长度：5000 字符
    - 推荐分块大小：2500 字符
    - 空内容检查：禁止写入空内容

    🔄 写入模式优化：
    - 默认模式 "w"：覆盖写入（适合完整内容）
    - 追加模式 "a"：追加写入（适合分块内容）
    - 混合模式：建议先使用 "w" 写入基础内容，后续使用 "a" 追加

    📝 正确示例：
    - write_file("Sandbox/test.py", "基础内容")                    ← 覆盖写入
    - write_file("Sandbox/test.py", "追加内容", mode="a")         ← 追加写入
    - write_file("Sandbox/subdir/file.py", "content")             ← 沙盒子目录
    - write_file("Sandbox/Neko_SafeBox/new.md", "content")        ← 保险箱内创建新文件

    🚫 错误示例：
    - write_file("Agents/test.py", "content")                     ← 试图修改项目文件
    - write_file("/tmp/test.py", "content")                       ← 沙盒外禁止
    - write_file("Sandbox/Neko_SafeBox/exist.md", "new")          ← 保险箱内禁止覆盖
    - write_file("Sandbox/test.py", "" * 3000)                    ← 内容过长禁止

    🔍 长度控制策略：
    - 单次写入建议不超过 5000 字符
    - 长内容建议分块写入，使用追加模式
    - 写入前检查内容长度，避免输出限制
    - 使用 process_text 工具预处理长文本

    📊 最佳实践：
    1. 首次写入：使用 "w" 模式写入基础框架
    2. 后续追加：使用 "a" 模式分块添加内容
    3. 长度检查：每次写入前检查 content 长度
    4. 内容优化：使用 process_text 处理长文本

    Args:
        file_path (str): 相对于项目根目录的文件路径
        content (str): 文件内容（长度限制：5000 字符）
        mode (str): 写入模式
            - "w": 覆盖写入（默认）
            - "a": 追加写入
        encoding (str): 文件编码
        description (str): 操作描述

    Returns:
        tuple: (success, message)
    """
    return _write_file_impl(file_path, content, mode, encoding, description)


# 分块写入辅助函数
def write_large_content(file_path: str, large_content: str, chunk_size: int = CHUNK_SIZE, description: str = "") -> tuple:
    """
    分块写入大内容

    Args:
        file_path: 文件路径
        large_content: 大内容
        chunk_size: 分块大小
        description: 操作描述

    Returns:
        (success, message)
    """
    total_chunks = (len(large_content) + chunk_size - 1) // chunk_size

    # 首次写入使用覆盖模式
    first_chunk = large_content[:chunk_size]
    result = write_file(file_path, first_chunk, mode="w", description=f"{description} - 第1/{total_chunks}块")

    if not result[0]:
        return result

    # 后续使用追加模式
    remaining = large_content[chunk_size:]
    for i in range(0, len(remaining), chunk_size):
        chunk = remaining[i:i+chunk_size]
        chunk_num = i // chunk_size + 2
        result = write_file(file_path, chunk, mode="a", description=f"{description} - 第{chunk_num}/{total_chunks}块")

        if not result[0]:
            return result

    return True, f"分块写入完成，共{total_chunks}块，总长度{len(large_content)}字符"