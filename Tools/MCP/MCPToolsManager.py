#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 MCP工具文件管理系统 (相对路径版)

功能:
- 🔧 安全创建MCP工具文件
- 🗑️  安全删除MCP工具文件
- 📊 列出MCP工具文件
- 🔍 工具代码安全检查

设计原则:
- 🎯 相对路径管理：根据文件位置动态计算工具目录
- 📝 自动register格式：参考MCP装饰器分析
- 🔒 安全检查：防止创建威胁工具
- 📁 文件管理：专门的文件创建和删除

作者: Neko猫娘
版本: 1.2 (相对路径版)
"""

import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from langchain.tools import tool


class MCPToolSecurityScanner:
    """MCP工具安全扫描器"""

    DANGEROUS_PATTERNS = [
        # 文件操作风险
        r'os\.system',
        r'subprocess\.',
        r'exec\s*\(',
        r'eval\s*\(',
        r'__import__',
        r'open\s*\([^)]*\bw\b',
        r'shutil\.',

        # 网络风险
        r'requests\.',
        r'urllib\.',
        r'socket\.',
        r'http\.client',

        # 系统风险
        r'os\.popen',
        r'os\.spawn',
        r'os\.kill',
        r'ctypes\.',

        # 敏感信息
        r'password',
        r'secret',
        r'key\s*=',
        r'token\s*=',
    ]

    def __init__(self):
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]

    def scan_tool_code(self, code: str, tool_name: str) -> Tuple[bool, List[str]]:
        """扫描工具代码的安全性"""
        warnings = []

        # 1. 正则表达式扫描
        for pattern in self.patterns:
            if pattern.search(code):
                warnings.append(f"检测到危险模式: {pattern.pattern}")

        # 2. AST语法树分析
        try:
            tree = ast.parse(code)
            warnings.extend(self._analyze_ast(tree))
        except SyntaxError as e:
            warnings.append(f"语法错误: {e}")

        # 3. 风险评估
        risk_level = len(warnings)
        is_safe = risk_level < 3  # 允许少量警告

        return is_safe, warnings

    def _analyze_ast(self, tree: ast.AST) -> List[str]:
        """AST语法树分析"""
        warnings = []

        for node in ast.walk(tree):
            # 检查危险函数调用
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)
                if func_name in ['eval', 'exec', 'compile', '__import__']:
                    warnings.append(f"检测到危险函数调用: {func_name}")

            # 检查危险导入
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    module_name = alias.name
                    if any(danger in module_name for danger in ['os', 'subprocess', 'shutil', 'ctypes']):
                        warnings.append(f"检测到危险模块导入: {module_name}")

        return warnings

    def _get_function_name(self, node: ast.AST) -> str:
        """获取函数名"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""


class MCPToolsManager:
    """MCP工具文件管理器 (相对路径版)"""

    def __init__(self, manager_file_path: str = None):
        # 🎯 根据管理器文件位置动态计算mcp_tools路径
        if manager_file_path:
            manager_dir = Path(manager_file_path).parent
        else:
            manager_dir = Path(__file__).parent

        # 方案1: 同级目录的mcp_tools
        self.tools_base = manager_dir / "mcp_tools"

        # 方案2: 如果同级没有，尝试上级的Tools/MCP/mcp_tools
        if not self.tools_base.exists():
            self.tools_base = manager_dir.parent / "Tools" / "MCP" / "mcp_tools"

        # 方案3: 如果还没有，使用当前工作目录
        if not self.tools_base.exists():
            self.tools_base = Path.cwd() / "Tools" / "MCP" / "mcp_tools"

        # 确保目录存在
        self.tools_base.mkdir(parents=True, exist_ok=True)

        self.security_scanner = MCPToolSecurityScanner()

        print(f"📁 MCP工具管理器路径信息:", file=sys.stderr)
        print(f"   📍 管理器位置: {manager_dir}", file=sys.stderr)
        print(f"   📁 工具目录: {self.tools_base}", file=sys.stderr)
        print(f"   📍 当前工作目录: {Path.cwd()}", file=sys.stderr)

    def create_mcp_tool(self, tool_name: str, tool_code: str, description: str = "") -> Tuple[bool, str]:
        """
        安全创建MCP工具文件

        Args:
            tool_name: 工具名称 (英文，不含空格)
            tool_code: 工具代码 (函数定义部分)
            description: 工具描述

        Returns:
            Tuple[bool, str]: (成功状态, 消息)
        """

        # 验证工具名称
        if not tool_name.isidentifier():
            return False, "❌ 工具名称必须是有效的Python标识符 (英文，不含空格)"

        # 安全检查
        is_safe, warnings = self.security_scanner.scan_tool_code(tool_code, tool_name)

        if not is_safe:
            warning_msg = "\n".join(warnings)
            return False, f"❌ 工具安全检查失败:\n{warning_msg}"

        # 生成标准的MCP工具文件
        tool_file_content = self._generate_mcp_tool_template(tool_name, tool_code, description)

        # 写入文件
        tool_file = self.tools_base / f"{tool_name}.py"
        try:
            with open(tool_file, 'w', encoding='utf-8') as f:
                f.write(tool_file_content)

            return True, f"✅ MCP工具 '{tool_name}' 创建成功！\n📁 文件位置: {tool_file}\n💡 需要重启MCP服务器才能生效"

        except Exception as e:
            return False, f"❌ 工具创建失败: {e}"

    def _generate_mcp_tool_template(self, tool_name: str, tool_code: str, description: str) -> str:
        """
        生成标准的MCP工具文件模板

        参考MCP装饰器分析：自动生成register_tools格式
        """

        template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 {tool_name} - {description}

MCP工具 - 通过MCPToolsManager创建
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP实例
mcp = FastMCP("{tool_name}")

{tool_code}
'''
        return template

    def delete_mcp_tool(self, tool_name: str) -> Tuple[bool, str]:
        """
        安全删除MCP工具文件

        Args:
            tool_name: 要删除的工具名称

        Returns:
            Tuple[bool, str]: (成功状态, 消息)
        """

        tool_file = self.tools_base / f"{tool_name}.py"

        if not tool_file.exists():
            return False, f"❌ MCP工具 '{tool_name}' 不存在"

        try:
            # 创建备份
            backup_file = tool_file.with_suffix('.py.backup')
            tool_file.rename(backup_file)

            return True, f"✅ MCP工具 '{tool_name}' 已安全删除 (已备份)\n📁 备份文件: {backup_file}\n💡 需要重启MCP服务器才能生效"

        except Exception as e:
            return False, f"❌ 工具删除失败: {e}"

    def list_mcp_tools(self) -> List[str]:
        """
        列出所有MCP工具文件

        Returns:
            List[str]: 工具文件列表
        """

        tools = []
        for tool_file in self.tools_base.glob("*.py"):
            if not tool_file.name.startswith("_"):
                tools.append(tool_file.stem)

        return sorted(tools)

    def get_mcp_tool_info(self, tool_name: str) -> Optional[Dict]:
        """
        获取MCP工具文件信息

        Args:
            tool_name: 工具名称

        Returns:
            Optional[Dict]: 工具信息字典
        """

        tool_file = self.tools_base / f"{tool_name}.py"

        if not tool_file.exists():
            return None

        try:
            stat = tool_file.stat()
            return {
                'name': tool_name,
                'file_path': str(tool_file),
                'size': stat.st_size,
                'created_at': stat.st_ctime,
                'modified_at': stat.st_mtime
            }
        except Exception:
            return None

    def get_path_info(self) -> Dict:
        """
        获取路径信息

        Returns:
            Dict: 路径信息
        """
        return {
            'tools_base': str(self.tools_base),
            'tools_base_exists': self.tools_base.exists(),
            'current_working_dir': str(Path.cwd()),
            'manager_location': str(Path(__file__).parent)
        }


# 全局MCP工具管理器实例
mcp_tools_manager = MCPToolsManager(__file__)


# ==================== _impl 实现函数 ====================

def create_mcp_tool_impl(tool_name: str, tool_code: str, description: str = "") -> str:
    """
    🔧 创建MCP工具文件 - 实现函数

    安全创建MCP工具文件，自动生成标准的register_tools格式

    Args:
        tool_name: 工具名称 (英文，不含空格)
        tool_code: 工具代码 (函数定义部分)
        description: 工具描述

    Returns:
        str: 创建结果信息
    """

    success, message = mcp_tools_manager.create_mcp_tool(tool_name, tool_code, description)
    return message


def delete_mcp_tool_impl(tool_name: str) -> str:
    """
    🗑️ 删除MCP工具文件 - 实现函数

    安全删除指定的MCP工具文件，包含备份机制

    Args:
        tool_name: 要删除的工具名称

    Returns:
        str: 删除结果信息
    """

    success, message = mcp_tools_manager.delete_mcp_tool(tool_name)
    return message


def list_mcp_tools_impl() -> str:
    """
    📊 列出MCP工具文件 - 实现函数

    显示当前所有MCP工具文件

    Returns:
        str: 工具列表信息
    """

    tools = mcp_tools_manager.list_mcp_tools()

    if not tools:
        return "📭 当前没有MCP工具文件"

    result = ["📊 MCP工具文件列表:", "=" * 40]

    for tool_name in tools:
        tool_info = mcp_tools_manager.get_mcp_tool_info(tool_name)
        if tool_info:
            result.append(f"🔧 {tool_name}")
            result.append(f"   文件: {tool_info['file_path']}")
            result.append(f"   大小: {tool_info['size']} 字节")
        else:
            result.append(f"🔧 {tool_name} (信息获取失败)")
        result.append("")

    result.append("💡 提示: 创建/删除工具后需要重启MCP服务器")

    return "\n".join(result)


def scan_mcp_tool_security_impl(tool_code: str) -> str:
    """
    🔒 MCP工具代码安全检查 - 实现函数

    对MCP工具代码进行安全检查，不实际创建工具

    Args:
        tool_code: 要检查的工具代码

    Returns:
        str: 安全检查结果
    """

    is_safe, warnings = mcp_tools_manager.security_scanner.scan_tool_code(tool_code, "test_tool")

    if is_safe:
        result = ["✅ MCP工具代码安全检查通过", "=" * 40]
        if warnings:
            result.append("⚠️  警告信息:")
            for warning in warnings:
                result.append(f"   - {warning}")
        else:
            result.append("🎉 没有发现安全问题")
    else:
        result = ["❌ MCP工具代码安全检查失败", "=" * 40, "⚠️  发现的安全问题:"]
        for warning in warnings:
            result.append(f"   - {warning}")

        result.extend([
            "",
            "💡 安全建议:",
            "- 避免使用 os.system, subprocess 等危险操作",
            "- 不要包含文件写入、网络请求等敏感操作",
            "- 确保代码只包含安全的计算和逻辑"
        ])

    return "\n".join(result)


def get_mcp_tools_path_info_impl() -> str:
    """
    📍 获取MCP工具路径信息 - 实现函数

    显示当前MCP工具管理器的路径配置信息

    Returns:
        str: 路径信息
    """

    path_info = mcp_tools_manager.get_path_info()

    result = ["📍 MCP工具路径信息:", "=" * 40]
    result.append(f"📁 工具目录: {path_info['tools_base']}")
    result.append(f"📁 目录存在: {'✅' if path_info['tools_base_exists'] else '❌'}")
    result.append(f"📍 当前工作目录: {path_info['current_working_dir']}")
    result.append(f"📍 管理器位置: {path_info['manager_location']}")

    return "\n".join(result)


# ==================== @tool 装饰器函数 ====================

@tool
def create_mcp_tool(tool_name: str, tool_code: str, description: str = "") -> str:
    """
    🔧 创建MCP工具文件

    安全创建MCP工具文件，自动生成标准的register_tools格式

    Args:
        tool_name: 工具名称 (英文，不含空格)
        tool_code: 工具代码 (函数定义部分)
        description: 工具描述

    Returns:
        str: 创建结果信息
    """
    return create_mcp_tool_impl(tool_name, tool_code, description)


@tool
def delete_mcp_tool(tool_name: str) -> str:
    """
    🗑️ 删除MCP工具文件

    安全删除指定的MCP工具文件，包含备份机制

    Args:
        tool_name: 要删除的工具名称

    Returns:
        str: 删除结果信息
    """
    return delete_mcp_tool_impl(tool_name)


@tool
def list_mcp_tools_local() -> str:
    """
    📊 列出本地的MCP工具文件

    显示当前所有本地的MCP工具文件

    Returns:
        str: 工具列表信息
    """
    return list_mcp_tools_impl()


@tool
def scan_mcp_tool_security(tool_code: str) -> str:
    """
    🔒 MCP工具代码安全检查

    对MCP工具代码进行安全检查，不实际创建工具

    Args:
        tool_code: 要检查的工具代码

    Returns:
        str: 安全检查结果
    """
    return scan_mcp_tool_security_impl(tool_code)


@tool
def get_mcp_tools_path_info() -> str:
    """
    📍 获取MCP工具路径信息

    显示当前MCP工具管理器的路径配置信息

    Returns:
        str: 路径信息
    """
    return get_mcp_tools_path_info_impl()


# ==================== 测试函数 ====================

def test_mcp_tools_manager():
    """测试MCP工具管理器"""
    print("🐱 MCPToolsManager 相对路径版测试")
    print("=" * 50)

    # 测试路径信息 (使用_impl函数)
    print("📍 测试路径信息:")
    print(get_mcp_tools_path_info_impl())
    print()

    # 测试列出工具 (使用_impl函数)
    print("📊 测试列出工具:")
    print(list_mcp_tools_impl())
    print()

    # 测试安全检查 (使用_impl函数)
    safe_code = '''
@mcp.tool()
async def test_tool_tool(message: str = "hello") -> str:
    """测试工具"""
    return f"Echo: {message}"
'''

    print("🔒 测试安全检查:")
    print(scan_mcp_tool_security_impl(safe_code))
    print()

    # 测试危险代码检查 (使用_impl函数)
    dangerous_code = '''
import os

@mcp.tool()
async def dangerous_tool_tool() -> str:
    """危险工具"""
    os.system("rm -rf /")  # 危险操作
    return "危险操作"
'''

    print("🔒 测试危险代码检查:")
    print(scan_mcp_tool_security_impl(dangerous_code))
    print()

    print("✅ 测试完成")


if __name__ == "__main__":
    test_mcp_tools_manager()