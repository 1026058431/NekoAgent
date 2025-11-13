#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP Streamable-HTTP客户端 - 基于官方MultiServerMCPClient

使用官方langchain-mcp-adapters库，专注于业务逻辑封装
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional

# 🔧 强制设置UTF-8编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 导入官方MCP客户端
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools


class MCPStreamableClient:
    """MCP Streamable-HTTP客户端 - 基于官方实现"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        self.server_url = server_url
        self.connected = False
        self.client = None
        self.tools = []
        
    async def connect(self) -> Dict[str, Any]:
        """连接到MCP服务器"""
        try:
            print(f"🔗 连接到MCP服务器: {self.server_url}", file=sys.stderr)
            
            # 使用官方MultiServerMCPClient
            self.client = MultiServerMCPClient(
                {
                    "mcp_server": {
                        "url": f"{self.server_url}/mcp",
                        "transport": "streamable_http",
                    }
                }
            )
            
            # 获取工具列表
            self.tools = await self.client.get_tools()
            self.connected = True
            
            print(f"✅ MCP服务器连接成功", file=sys.stderr)
            print(f"🔧 发现 {len(self.tools)} 个工具", file=sys.stderr)
            
            return {
                "success": True,
                "message": "MCP服务器连接成功",
                "server_url": self.server_url,
                "tools_count": len(self.tools)
            }
            
        except Exception as e:
            print(f"❌ 连接失败: {e}", file=sys.stderr)
            return {
                "success": False,
                "error": f"连接失败: {e}"
            }
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        if not self.connected:
            return {
                "success": False,
                "error": "未连接到MCP服务器"
            }
        
        tool_names = [tool.name for tool in self.tools]
        
        return {
            "success": True,
            "tools": tool_names,
            "count": len(tool_names)
        }
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        if not self.connected:
            return {
                "success": False,
                "error": "未连接到MCP服务器"
            }
        
        try:
            # 查找对应的工具
            target_tool = None
            for tool in self.tools:
                if tool.name == tool_name:
                    target_tool = tool
                    break
            
            if not target_tool:
                return {
                    "success": False,
                    "error": f"工具 '{tool_name}' 不存在"
                }
            
            print(f"🔧 调用工具: {tool_name}", file=sys.stderr)
            print(f"📦 参数: {parameters}", file=sys.stderr)
            
            # 调用工具
            result = await target_tool.ainvoke(parameters)
            
            print(f"📥 结果: {result}", file=sys.stderr)
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }
            
        except Exception as e:
            print(f"❌ 工具调用失败: {e}", file=sys.stderr)
            return {
                "success": False,
                "error": f"工具调用失败: {e}"
            }
    
    async def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        if not self.connected:
            return {
                "success": False,
                "error": "未连接到MCP服务器"
            }
        
        return {
            "success": True,
            "server_info": {
                "server_url": self.server_url,
                "connected": True,
                "tools_count": len(self.tools),
                "transport": "streamable-http"
            }
        }


# 创建全局客户端实例
_client_impl = MCPStreamableClient()


# ========== 给neko调用的工具函数 ==========

from langchain.tools import tool


@tool
def connect_mcp_server(server_url: str = "http://127.0.0.1:8000") -> Dict[str, Any]:
    """
    连接到指定URL的MCP服务器

    Args:
        server_url: MCP服务器URL，默认 http://127.0.0.1:8000

    Returns:
        dict: 连接结果
    """
    global _client_impl
    _client_impl = MCPStreamableClient(server_url)
    return asyncio.run(_client_impl.connect())


@tool
def list_mcp_tools() -> Dict[str, Any]:
    """
    列出MCP服务器中的可用工具

    Returns:
        dict: 工具列表
    """
    return asyncio.run(_client_impl.list_tools())


@tool
def call_mcp_tool(tool_name: str, tool_args: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    调用MCP服务器中的工具

    ⚠️ 重要：所有MCP工具参数必须通过tool_args字典传递

    Args:
        tool_name: 工具名称
        tool_args: 工具参数字典，格式如 {"text": "hello"} 或 {"a": 10, "b": 5}

    Examples:
        ✅ call_mcp_tool("echo", tool_args={"text": "hello"})
        ✅ call_mcp_tool("add_numbers", tool_args={"a": 10, "b": 5})
        ❌ call_mcp_tool("echo", text="hello")  # 错误！参数会丢失
    """
    parameters = tool_args or {}
    return asyncio.run(_client_impl.call_tool(tool_name, parameters))


@tool
def get_mcp_server_info() -> Dict[str, Any]:
    """
    获取MCP服务器信息

    Returns:
        dict: 服务器信息
    """
    return asyncio.run(_client_impl.get_server_info())


# ========== 测试函数 ==========

async def test_mcp_client():
    """测试MCP客户端功能"""
    print("🐱 测试MCP Streamable-HTTP客户端...")
    
    # 使用_impl实例直接测试
    client = MCPStreamableClient("http://127.0.0.1:8000")
    
    # 1. 连接到服务器
    print("\n1. 连接到服务器...")
    connect_result = await client.connect()
    print(f"   结果: {connect_result}")
    
    if connect_result["success"]:
        # 2. 获取服务器信息
        print("\n2. 获取服务器信息...")
        info_result = await client.get_server_info()
        print(f"   结果: {info_result}")
        
        # 3. 列出工具
        print("\n3. 列出工具...")
        tools_result = await client.list_tools()
        print(f"   结果: {tools_result}")
        
        # 4. 调用echo工具
        print("\n4. 调用echo工具...")
        echo_result = await client.call_tool("echo", {"text": "Hello from MCP client!"})
        print(f"   结果: {echo_result}")
        
        # 5. 调用add_numbers工具
        print("\n5. 调用add_numbers工具...")
        add_result = await client.call_tool("add_numbers", {"a": 10, "b": 5})
        print(f"   结果: {add_result}")
        
        # 6. 调用calculator工具
        print("\n6. 调用calculator工具...")
        calc_result = await client.call_tool("calculator", {"operation": "multiply", "a": 6, "b": 7})
        print(f"   结果: {calc_result}")

    print("\n测试完成!")


# 使用指南
def mcp_server_usage_guide() -> str:
    """
    获取MCP服务器使用指南

    Returns:
        str: 使用指南
    """
    return """
🐱 MCP服务器使用指南（Streamable-HTTP版）
═══════════════════════════════

📋 手动启动服务器：
   $ python mcp_server_streamable.py --port 8000

📋 连接到服务器：
   connect_mcp_server("http://127.0.0.1:8000")

📋 使用工具：
   - list_mcp_tools() - 列出可用工具
   - call_mcp_tool("echo", tool_args={"text": "hello"}) - 调用工具
   - get_mcp_server_info() - 获取服务器信息

⚠️ 重要提醒：
   - 服务器必须手动启动
   - 使用HTTP协议 (http://)
   - 参数必须通过tool_args字典传递
   - 支持动态工具加载
═══════════════════════════════
    """


if __name__ == "__main__":
    # 显示使用指南
    print(mcp_server_usage_guide())
    
    # 运行异步测试
    asyncio.run(test_mcp_client())