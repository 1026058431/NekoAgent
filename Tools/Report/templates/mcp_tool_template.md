#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 MCP工具创建模板 - 标准格式

用于指导LLM正确创建和注册MCP工具的标准模板

## 🎯 模板使用说明

### 1. 基础结构
- 必须包含 `register_tools` 函数
- 使用 `@mcp.tool()` 装饰器
- 包含完整的文档字符串

### 2. 安全要求
- 避免危险操作 (os.system, subprocess等)
- 添加适当的权限检查
- 模糊错误信息，不泄露敏感数据

### 3. 代码规范
- 使用类型注解
- 包含完整的参数说明
- 返回结构化的数据
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP实例 - 工具名称应该有意义
mcp = FastMCP("tool_name")


@mcp.tool()
async def tool_function_name(param1: str, param2: int = 0) -> dict:
    """
    工具功能描述
    
    详细描述工具的功能、用途和使用场景
    
    Args:
        param1 (str): 参数1的详细说明
        param2 (int, optional): 参数2的详细说明，默认值
        
    Returns:
        dict: 返回数据的结构说明
        
    Example:
        >>> await tool_function_name("test", 42)
        {"result": "success", "data": {...}}
        
    Security Note:
        - 此工具只进行安全的读取操作
        - 不执行任何危险的系统调用
        - 错误信息经过模糊处理
    """
    try:
        # 工具实现逻辑
        # 避免使用危险操作：os.system, subprocess, eval等
        
        result = {
            "success": True,
            "result": "操作成功",
            "data": {
                "param1": param1,
                "param2": param2
            }
        }
        
        return result
        
    except Exception as e:
        # 错误信息模糊处理，不泄露敏感信息
        return {
            "success": False,
            "error": "操作失败",
            "details": "请检查输入参数"
        }


# 🎯 必须包含的注册函数
def register_tools(mcp_instance):
    """
    注册工具到MCP服务器
    
    这个函数是必须的，MCP服务器通过这个函数加载工具
    
    Args:
        mcp_instance: MCP服务器实例
    """
    # 注册工具到传入的MCP实例
    mcp_instance.add_tool(tool_function_name, name="tool_function_name")


# 可选：工具加载完成提示
print(f"🐱 MCP工具 'tool_name' 文件加载完成")


# ============================================================================
# 🎯 安全工具示例 - 带路径检查的文件操作
# ============================================================================

class PathSecurity:
    """路径安全检查器"""
    
    # 允许访问的路径前缀
    ALLOWED_PATHS = [
        "mcp_tools/",
        "Tools/MCP/", 
        "Sandbox/",
        "test",
        "demo"
    ]
    
    @classmethod
    def is_path_allowed(cls, file_path: str) -> bool:
        """检查路径是否在允许范围内"""
        for allowed_path in cls.ALLOWED_PATHS:
            if file_path.startswith(allowed_path):
                return True
        return False


@mcp.tool()
async def secure_file_operation(file_path: str) -> dict:
    """
    安全的文件操作示例
    
    演示如何添加路径安全检查
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 操作结果
    """
    import os
    
    # 路径安全检查
    if not PathSecurity.is_path_allowed(file_path):
        return {"error": "权限不足: 路径不在允许范围内"}
    
    if not os.path.exists(file_path):
        return {"error": "文件不存在"}
    
    try:
        # 安全的文件操作
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "file_size": len(content),
            "line_count": len(content.split('\n')),
            "security_note": "此操作经过路径安全检查"
        }
        
    except Exception:
        return {"error": "读取文件失败"}


# ============================================================================
# 🎯 工具创建检查清单
# ============================================================================

"""
✅ MCP工具创建检查清单

1. 🎯 基础结构
   [ ] 包含 register_tools 函数
   [ ] 使用 @mcp.tool() 装饰器
   [ ] 有完整的文档字符串

2. 🛡️ 安全要求
   [ ] 避免危险操作 (os.system, subprocess, eval)
   [ ] 添加适当的权限检查
   [ ] 错误信息模糊处理

3. 📝 代码规范
   [ ] 使用类型注解
   [ ] 参数说明完整
   [ ] 返回结构化数据

4. 🔧 功能设计
   [ ] 工具名称有意义
   [ ] 功能单一明确
   [ ] 错误处理完善

5. 🐱 风格要求
   [ ] 包含neko风格的注释
   [ ] 使用emoji增强可读性
   [ ] 有工具加载完成提示
"""