"""
🐱 修复版报告工具 - 直接返回模板内容，包含可用模板列表

🎯 设计理念：直接返回模板文件内容，错误时显示可用模板
"""

from langchain.tools import tool
import os
from pathlib import Path

@tool
def list_all_templates():
    """
    列出所有可用的模板文件

    Returns:
        模板文件名称列表
    """
    try:
        current_dir = Path(__file__).parent
        templates_dir = current_dir / "templates"

        templates = []
        for file_path in templates_dir.glob("*.md"):
            if file_path.is_file():
                templates.append(file_path.stem)

        return templates

    except Exception as e:
        return []

@tool
def get_report_template(template_name: str):
    """
    获取指定模板的完整内容

    Args:
        template_name: 模板文件名称（不含扩展名）

    Returns:
        模板文件的完整内容字符串，错误时包含可用模板列表
    """
    try:
        # 获取当前文件所在目录
        current_dir = Path(__file__).parent
        templates_dir = current_dir / "templates"

        # 构建模板文件路径
        template_path = templates_dir / f"{template_name}.md"

        # 检查文件是否存在
        if not template_path.exists():
            available_templates = list_all_templates()
            error_msg = f"""❌ 错误：未找到模板文件 '{template_name}.md'

📋 可用模板列表：
{chr(10).join(f'- {t}' for t in available_templates)}

💡 请从以上模板中选择一个使用"""
            return error_msg

        # 读取并返回模板内容
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content

    except Exception as e:
        available_templates = list_all_templates()
        error_msg = f"""❌ 错误：读取模板文件失败 - {str(e)}

📋 可用模板列表：
{chr(10).join(f'- {t}' for t in available_templates)}

💡 请从以上模板中选择一个使用"""
        return error_msg


@tool
def add_new_template(file_path: str, template_name: str = None):
    """
    添加新的模板文件 - 安全修复版

    Args:
        file_path: 模板文件路径（必须在沙盒内，相对于项目根目录）
        template_name: 模板名称（可选）

    Returns:
        str: 操作结果消息
    """
    try:
        current_dir = Path(__file__).parent
        templates_dir = current_dir / "templates"

        # 获取项目根目录（Tools目录的父目录）
        project_root = current_dir.parent.parent

        # 1. 路径安全验证 - 基于项目根目录
        # 构建相对于项目根目录的完整路径
        source_path = project_root / file_path

        # 验证文件路径在沙盒范围内
        if not file_path.replace("\\", "/").startswith("Sandbox/"):
            return "❌ 安全错误：文件必须在沙盒目录内，使用 'Sandbox/文件名' 格式"

        # 验证文件确实存在
        if not source_path.exists():
            return f"❌ 文件不存在：{file_path}"

        # 验证是文件而不是目录
        if not source_path.is_file():
            return f"❌ 路径不是文件：{file_path}"

        # 2. 文件名安全处理
        import re

        # 如果提供了模板名称，使用安全的名称
        if template_name:
            # 移除危险字符，只允许字母、数字、下划线、连字符
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', template_name)
            if not safe_name:
                return "❌ 模板名称包含无效字符，只允许字母、数字、下划线、连字符"
        else:
            # 使用源文件名（安全处理）
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', source_path.stem)
            if not safe_name:
                return "❌ 源文件名包含无效字符，无法用作模板名称"

        # 3. 目标路径构建
        target_path = templates_dir / f"{safe_name}.md"

        # 检查目标文件是否已存在
        if target_path.exists():
            return f"❌ 模板 '{safe_name}' 已存在，请使用其他名称"

        # 4. 安全复制文件
        import shutil
        shutil.copy2(source_path, target_path)

        return f"✅ 模板 '{safe_name}' 添加成功"

    except PermissionError:
        return "❌ 权限错误：无法访问文件"
    except OSError as e:
        return f"❌ 系统错误：{str(e)}"
    except Exception as e:
        return f"❌ 未知错误：{str(e)}"


# 测试函数
def test_fixed_template():
    """测试修复版模板工具"""
    print("🐱 修复版模板工具测试")
    print("=" * 50)

    # 列出所有模板
    templates = list_all_templates()
    print(f"可用模板文件: {templates}")
    print()

    # 获取CTF报告模板内容
    ctf_content = get_report_template("ctf_report_template")
    print("CTF报告模板内容:")
    print("=" * 30)
    print(ctf_content[:300] + "..." if len(ctf_content) > 300 else ctf_content)
    print()

    # 测试不存在的模板
    unknown_content = get_report_template("unknown_template")
    print("未知模板测试:")
    print(unknown_content)
    print()

    return True


if __name__ == "__main__":
    test_fixed_template()