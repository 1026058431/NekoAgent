#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 安全版MCP服务器 - 添加权限限制

在服务器层面限制危险的文件操作，防止路径逃逸
"""

import os
import sys
from pathlib import Path
import importlib.util

# 🔧 强制设置UTF-8编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("SecureMCPServer")


class SecurityManager:
    """安全管理器 - 限制危险的文件操作"""

    def __init__(self, allowed_base_paths: list):
        """
        初始化安全管理器

        Args:
            allowed_base_paths: 允许访问的基础路径列表
        """
        self.allowed_base_paths = [Path(path).resolve() for path in allowed_base_paths]

        print(f"🐱 安全管理器初始化 - 允许路径:", file=sys.stderr)
        for path in self.allowed_base_paths:
            print(f"  ✅ {path}", file=sys.stderr)

    def is_path_allowed(self, file_path: str) -> bool:
        """
        检查路径是否在允许范围内

        Args:
            file_path: 要检查的文件路径

        Returns:
            bool: 是否允许访问
        """
        try:
            path = Path(file_path).resolve()

            # 检查是否在任意允许的基础路径下
            for allowed_path in self.allowed_base_paths:
                if str(path).startswith(str(allowed_path)):
                    return True

            # 路径不在允许范围内
            print(f"🚫 安全阻止: 路径 {file_path} -> {path} 不在允许范围内", file=sys.stderr)
            return False

        except Exception as e:
            print(f"🚫 安全阻止: 路径解析失败 {file_path}: {e}", file=sys.stderr)
            return False

    def safe_file_operation(self, file_path: str, operation: callable, operation_type: str = "read") -> dict:
        """
        安全的文件操作包装器

        Args:
            file_path: 文件路径
            operation: 文件操作函数
            operation_type: 操作类型 (read/write/delete)

        Returns:
            dict: 操作结果
        """
        # 安全检查
        if not self.is_path_allowed(file_path):
            return {"error": "权限不足: 路径不在允许范围内"}

        # 写入操作额外检查
        if operation_type in ["write", "delete", "move"]:
            return {"error": "权限不足: 写入操作被禁止"}

        try:
            result = operation(file_path)
            return {"success": True, "result": result}
        except Exception as e:
            # 不泄露敏感信息
            if "No such file" in str(e) or "文件不存在" in str(e):
                return {"error": "文件不存在"}
            elif "Permission" in str(e):
                return {"error": "权限不足"}
            else:
                return {"error": "操作失败"}


class SecureToolLoader:
    """安全工具加载器 - 带权限限制"""

    def __init__(self, server_file_path: str, security_manager: SecurityManager):
        self.security_manager = security_manager

        # 🎯 根据服务器文件位置动态计算mcp_tools路径
        server_dir = Path(server_file_path).parent

        # 方案1: 同级目录的mcp_tools
        self.tools_base = server_dir / "mcp_tools"

        # 方案2: 如果同级没有，尝试上级的Tools/MCP/mcp_tools
        if not self.tools_base.exists():
            self.tools_base = server_dir.parent / "Tools" / "MCP" / "mcp_tools"

        # 方案3: 如果还没有，使用当前工作目录
        if not self.tools_base.exists():
            self.tools_base = Path.cwd() / "Tools" / "MCP" / "mcp_tools"

        # 确保目录存在
        self.tools_base.mkdir(parents=True, exist_ok=True)

        print(f"📁 工具目录: {self.tools_base}", file=sys.stderr)
        print(f"📁 服务器位置: {server_dir}", file=sys.stderr)

    def load_all_tools(self):
        """加载所有工具"""
        print(f"🔧 从 {self.tools_base} 加载工具...", file=sys.stderr)

        tool_count = 0

        # 只加载mcp_tools目录下的工具
        for tool_file in self.tools_base.glob("*.py"):
            if tool_file.name.startswith("_"):
                continue  # 跳过以_开头的文件

            tool_name = tool_file.stem
            if self._register_tool_from_file(tool_file, tool_name):
                tool_count += 1
                print(f"  📦 加载工具: {tool_name}", file=sys.stderr)

        print(f"✅ 共加载 {tool_count} 个工具", file=sys.stderr)
        return tool_count

    def _register_tool_from_file(self, file_path: Path, tool_name: str) -> bool:
        """从文件注册工具 - 使用注册函数方式"""
        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(tool_name, file_path)
            if spec is None or spec.loader is None:
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 强制要求必须有register_tools函数
            if hasattr(module, 'register_tools'):
                # 调用注册函数
                module.register_tools(mcp)
                return True
            else:
                print(f"❌ 工具 {tool_name} 缺少register_tools函数，跳过加载", file=sys.stderr)
                return False

        except Exception as e:
            print(f"❌ 加载工具 {tool_name} 失败: {e}", file=sys.stderr)
            return False


# 初始化安全管理器
# 只允许访问MCP工具目录和沙盒目录
security_manager = SecurityManager([
    Path(__file__).parent,  # 服务器所在目录
    Path(__file__).parent / "mcp_tools",  # 工具目录
    Path(__file__).parent.parent.parent / "Sandbox"  # 沙盒目录
])


# 基础工具定义 - 安全版本
@mcp.tool()
async def echo(text: str) -> str:
    """
    回显输入的文本

    Args:
        text: 要回显的文本

    Returns:
        str: 回显结果
    """
    return f"Echo: {text}"


@mcp.tool()
async def add_numbers(a: int, b: int) -> int:
    """
    两个数字相加

    Args:
        a: 第一个数字
        b: 第二个数字

    Returns:
        int: 相加结果
    """
    return a + b


@mcp.tool()
async def get_server_info() -> dict:
    """
    获取服务器信息

    Returns:
        dict: 服务器信息
    """
    return {
        "server_name": "SecureMCPServer",
        "protocol": "MCP",
        "transport": "streamable-http",
        "host": "127.0.0.1",
        "port": 8000,
        "security_level": "restricted",
        "allowed_operations": ["read"],
        "blocked_operations": ["write", "delete", "move"]
    }


@mcp.tool()
async def secure_file_stats(file_path: str) -> dict:
    """
    安全的文件统计工具

    在权限限制下统计文件信息

    Args:
        file_path: 要统计的文件路径

    Returns:
        dict: 包含文件统计信息的字典
    """

    def _stats_operation(path):
        if not os.path.exists(path):
            return {"error": "文件不存在"}

        if not os.path.isfile(path):
            return {"error": "不是文件"}

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            file_info = os.stat(path)

            return {
                "file_path": path,
                "file_size": file_info.st_size,
                "line_count": len(lines),
                "char_count": len(content),
                "word_count": len(content.split()),
                "non_empty_lines": len([line for line in lines if line.strip()]),
                "created_time": file_info.st_ctime,
                "modified_time": file_info.st_mtime
            }
        except Exception:
            return {"error": "读取文件失败"}

    return security_manager.safe_file_operation(file_path, _stats_operation, "read")


@mcp.tool()
async def list_available_tools() -> list:
    """
    列出所有可用工具

    Returns:
        list: 工具名称列表
    """
    tools = ["echo", "add_numbers", "get_server_info", "list_available_tools", "secure_file_stats"]

    # 添加动态加载的工具
    for tool_file in tool_loader.tools_base.glob("*.py"):
        if not tool_file.name.startswith("_"):
            tools.append(tool_file.stem)

    return tools


@mcp.tool()
async def get_tools_directory_info() -> dict:
    """
    获取工具目录信息

    Returns:
        dict: 目录信息
    """
    tools_dir = tool_loader.tools_base
    tools = []

    for tool_file in tools_dir.glob("*.py"):
        if not tool_file.name.startswith("_"):
            tools.append({
                "name": tool_file.stem,
                "file": tool_file.name,
                "size": tool_file.stat().st_size,
                "modified": tool_file.stat().st_mtime
            })

    return {
        "directory": str(tools_dir),
        "exists": tools_dir.exists(),
        "tools_count": len(tools),
        "tools": tools,
        "server_location": str(Path(__file__).parent),
        "current_working_dir": str(Path.cwd()),
        "security_info": "所有文件操作都经过权限检查"
    }


@mcp.tool()
async def debug_path_info() -> dict:
    """
    调试路径信息

    Returns:
        dict: 路径调试信息
    """
    server_file = Path(__file__)

    return {
        "server_file": str(server_file),
        "server_dir": str(server_file.parent),
        "tools_base": str(tool_loader.tools_base),
        "current_working_dir": str(Path.cwd()),
        "security_manager": {
            "allowed_paths": [str(path) for path in security_manager.allowed_base_paths],
            "security_level": "restricted",
            "blocked_operations": ["write", "delete", "move"]
        }
    }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='安全版MCP服务器')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口 (默认: 8000)')
    parser.add_argument('--host', default='127.0.0.1', help='绑定地址 (默认: 127.0.0.1)')

    args = parser.parse_args()

    # 初始化安全工具加载器
    global tool_loader
    tool_loader = SecureToolLoader(__file__, security_manager)

    # 加载工具
    tool_count = tool_loader.load_all_tools()

    print(f"🚀 启动安全版MCP服务器...", file=sys.stderr)
    print(f"📍 地址: {args.host}:{args.port}", file=sys.stderr)
    print(f"📁 工具文件夹: {tool_loader.tools_base}", file=sys.stderr)
    print(f"🔧 加载工具数: {tool_count + 7}", file=sys.stderr)  # +7 基础工具
    print("🎯 安全模式: 权限限制", file=sys.stderr)
    print("🚫 禁止操作: 写入、删除、移动", file=sys.stderr)
    print("⏹️  按 Ctrl+C 停止服务器", file=sys.stderr)

    try:
        # 启动MCP服务器
        mcp.run(
            transport="streamable-http",
        )
    except KeyboardInterrupt:
        print("\n🛑 服务器被用户中断", file=sys.stderr)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()