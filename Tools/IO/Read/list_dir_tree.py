"""
统一基准的目录浏览工具

使用项目根目录作为路径基准，与写入工具保持一致
"""

import os
import json
from langchain.tools import tool
from Tools.IO.core import security, utils


def _list_dir_tree_impl(path: str = None, depth: int = 2) -> str:
    """
    统一基准的目录树实现函数 - 项目范围

    Args:
        path (str): 相对于项目根目录的路径，默认项目根目录
        depth (int): 递归深度，默认2

    Returns:
        str: JSON格式的目录结构
    """
    try:
        # 安全检查1：确保目标路径在项目范围内
        if path:
            abs_path = security.validate_project_path(path)
            if not abs_path:
                return json.dumps({"error": f"路径 '{path}' 不在项目范围内"}, ensure_ascii=False, indent=2)
        else:
            abs_path = security.validate_project_path(".")

        # 安全检查2：敏感路径检查
        if security.is_sensitive_path(abs_path):
            return json.dumps({"error": f"不允许浏览敏感路径 '{os.path.basename(abs_path)}'"}, ensure_ascii=False, indent=2)

        # 安全检查3：路径存在性检查
        if not os.path.exists(abs_path):
            return json.dumps({"error": f"路径不存在：{abs_path}"}, ensure_ascii=False, indent=2)

        # 安全检查4：确保是目录
        if not os.path.isdir(abs_path):
            return json.dumps({"error": f"路径不是目录：{abs_path}"}, ensure_ascii=False, indent=2)

        def build_tree(current_path: str, current_depth: int) -> dict:
            """递归构建目录树"""
            name = os.path.basename(current_path)

            if os.path.isfile(current_path):
                return {
                    "name": name,
                    "type": "file",
                    "path": current_path
                }

            tree = {
                "name": name,
                "type": "dir",
                "path": current_path,
                "children": []
            }

            # 达到深度限制时停止递归
            if current_depth >= depth:
                return tree

            try:
                for item in os.listdir(current_path):
                    item_path = os.path.join(current_path, item)

                    # 跳过敏感路径
                    if security.is_sensitive_path(item_path):
                        continue

                    # 跳过隐藏文件和目录
                    if item.startswith('.'):
                        continue

                    tree["children"].append(build_tree(item_path, current_depth + 1))
            except PermissionError:
                # 没有权限访问的目录，跳过
                pass

            return tree

        # 构建目录树
        tree = build_tree(abs_path, 0)

        # 记录操作日志
        utils.log_operation("LIST_DIR", abs_path, f"depth={depth}", 0)

        return json.dumps(tree, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": f"浏览目录时发生错误：{e}"}, ensure_ascii=False, indent=2)


@tool
def list_dir_tree(path: str = None, depth: int = 2) -> str:
    """
    【权限说明】统一基准的目录浏览工具

    🐱 猫猫权限：查看允许的目录结构（项目范围，统一基准）

    ✅ 允许查看：
    - 沙盒目录及其子目录
    - 项目根目录（只读）
    - 其他明确允许的路径

    ❌ 禁止查看：
    - 系统敏感目录
    - 项目外的其他目录
    - 深度过深的目录结构

    📋 参数说明：
    - path (str): 相对于项目根目录的路径，默认项目根目录
    - depth (int): 递归深度，默认2
      - depth=1: 只显示当前目录的直接子项
      - depth=2: 显示当前目录及其直接子目录的内容
      - depth=3+: 显示更深层次的内容

    ⚠️ 重要警告：
    - 深度不足可能导致误判目录为空
    - 看起来空的目录可能包含深层文件
    - 删除前务必使用足够深度验证

    🎯 最佳实践：
    - 常规检查：使用depth=3确保看到完整结构
    - 深度探索：复杂目录使用depth=4或更高
    - 删除确认：删除前使用足够深度验证

    📝 正确示例：
    - list_dir_tree()                    ← 查看项目根目录(depth=2)
    - list_dir_tree("Sandbox")           ← 查看沙盒目录(depth=2)
    - list_dir_tree("Sandbox", depth=3)  ← 深度查看沙盒目录
    - list_dir_tree("Tools", depth=4)    ← 深度探索工具目录

    Args:
        path (str): 相对于项目根目录的路径，默认项目根目录
        depth (int): 递归深度，默认2

    Returns:
        str: JSON格式的目录结构
    """
    return _list_dir_tree_impl(path, depth)