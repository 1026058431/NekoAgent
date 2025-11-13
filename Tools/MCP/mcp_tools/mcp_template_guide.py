#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 mcp_template_guide - 提供MCP工具创建模板、常见问题避免和代码验证功能

MCP工具 - 通过MCPToolsManager创建
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP实例
mcp = FastMCP("mcp_template_guide")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 MCP模板指导工具 - 提供MCP工具创建指导和常见问题避免

帮助LLM正确创建MCP工具，避免常见的错误和陷阱
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP实例
mcp = FastMCP("mcp_template_guide")


@mcp.tool()
async def get_mcp_template(template_type: str = "basic") -> dict:
    """
    获取MCP工具创建模板
    
    提供不同类型的MCP工具模板，帮助正确创建工具
    
    Args:
        template_type: 模板类型
            - "basic": 基础工具模板
            - "secure": 安全工具模板
            - "file": 文件操作工具模板
            - "network": 网络工具模板
            
    Returns:
        dict: 包含模板代码和说明的字典
    """
    
    templates = {
        "basic": {
            "name": "基础MCP工具模板",
            "description": "最简单的MCP工具模板，包含必须的结构",
            "code": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 基础MCP工具模板

必须包含 register_tools 函数，使用 @mcp.tool() 装饰器
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP实例
mcp = FastMCP("tool_name")


@mcp.tool()
async def tool_function(param1: str, param2: int = 0) -> dict:
    """
    工具功能描述
    
    Args:
        param1: 参数1说明
        param2: 参数2说明，默认值
        
    Returns:
        dict: 返回结果
    """
    try:
        # 工具实现逻辑
        result = {
            "success": True,
            "result": f"处理完成: {param1}, {param2}"
        }
        return result
        
    except Exception:
        return {"error": "操作失败"}


# 🎯 必须包含的注册函数
def register_tools(mcp_instance):
    """注册工具到MCP服务器"""
    mcp_instance.add_tool(tool_function, name="tool_function")


print(f"🐱 MCP工具 'tool_name' 加载完成")'''
        },
        
        "secure": {
            "name": "安全MCP工具模板",
            "description": "带安全检查的MCP工具模板，防止路径逃逸等攻击",
            "code": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 安全MCP工具模板 - 带路径安全检查

防止路径逃逸攻击，添加权限检查
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP实例
mcp = FastMCP("secure_tool")


class PathSecurity:
    """路径安全检查器"""
    
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
    安全的文件操作
    
    Args:
        file_path: 文件路径
        
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
            "security_note": "此操作经过路径安全检查"
        }
        
    except Exception:
        return {"error": "读取文件失败"}


def register_tools(mcp_instance):
    """注册工具到MCP服务器"""
    mcp_instance.add_tool(secure_file_operation, name="secure_file_operation")


print(f"🐱 安全MCP工具 'secure_tool' 加载完成")'''
        },
        
        "file": {
            "name": "文件操作MCP工具模板",
            "description": "专门用于文件操作的MCP工具模板",
            "code": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🐱 文件操作MCP工具模板

专门用于文件读取、统计等操作的工具模板
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP实例
mcp = FastMCP("file_operations")


@mcp.tool()
async def file_stats(file_path: str) -> dict:
    """
    文件统计信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        dict: 文件统计信息
    """
    import os
    
    if not os.path.exists(file_path):
        return {"error": "文件不存在"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        file_info = os.stat(file_path)
        
        return {
            "file_path": file_path,
            "file_size": file_info.st_size,
            "line_count": len(lines),
            "char_count": len(content),
            "word_count": len(content.split()),
            "non_empty_lines": len([line for line in lines if line.strip()])
        }
        
    except Exception:
        return {"error": "读取文件失败"}


def register_tools(mcp_instance):
    """注册工具到MCP服务器"""
    mcp_instance.add_tool(file_stats, name="file_stats")


print(f"🐱 文件操作MCP工具 'file_operations' 加载完成")'''
        }
    }
    
    if template_type not in templates:
        return {
            "error": f"未知模板类型: {template_type}",
            "available_types": list(templates.keys())
        }
    
    return templates[template_type]


@mcp.tool()
async def get_common_issues() -> dict:
    """
    获取MCP工具创建常见问题和避免方法
    
    Returns:
        dict: 常见问题列表和解决方案
    """
    
    issues = {
        "常见问题": [
            {
                "issue": "缺少 register_tools 函数",
                "description": "MCP服务器必须通过register_tools函数加载工具",
                "solution": "确保每个工具文件都包含register_tools函数"
            },
            {
                "issue": "使用 @tool 装饰器而不是 @mcp.tool()",
                "description": "Langchain的@tool装饰器在MCP中无效",
                "solution": "使用 @mcp.tool() 装饰器定义工具函数"
            },
            {
                "issue": "危险操作导致安全警告",
                "description": "使用os.system、subprocess等危险操作",
                "solution": "避免危险操作，使用安全的替代方案"
            },
            {
                "issue": "路径逃逸安全风险",
                "description": "允许访问系统敏感文件",
                "solution": "添加路径安全检查，限制可访问的目录"
            },
            {
                "issue": "错误信息泄露敏感数据",
                "description": "详细的错误信息可能泄露系统信息",
                "solution": "模糊错误信息，不泄露具体错误细节"
            }
        ],
        "必须包含的内容": [
            "from mcp.server.fastmcp import FastMCP",
            "mcp = FastMCP('tool_name')",
            "@mcp.tool() 装饰器",
            "register_tools 函数",
            "工具加载完成提示"
        ],
        "必须避免的内容": [
            "@tool 装饰器 (Langchain专用)",
            "os.system、subprocess等危险操作",
            "eval、exec等代码执行函数",
            "详细的错误信息泄露",
            "无限制的文件路径访问"
        ]
    }
    
    return issues


@mcp.tool()
async def validate_mcp_code(code_snippet: str) -> dict:
    """
    验证MCP工具代码的正确性
    
    Args:
        code_snippet: 要验证的代码片段
        
    Returns:
        dict: 验证结果和建议
    """
    
    checks = {
        "has_fastmcp_import": "from mcp.server.fastmcp import FastMCP" in code_snippet,
        "has_mcp_instance": "mcp = FastMCP" in code_snippet,
        "has_mcp_tool_decorator": "@mcp.tool()" in code_snippet,
        "has_register_tools": "register_tools" in code_snippet,
        "has_dangerous_operations": any(op in code_snippet for op in ["os.system", "subprocess", "eval", "exec"]),
        "has_langchain_tool": "@tool" in code_snippet and "@mcp.tool()" not in code_snippet
    }
    
    issues = []
    suggestions = []
    
    if not checks["has_fastmcp_import"]:
        issues.append("缺少必要的导入: from mcp.server.fastmcp import FastMCP")
    
    if not checks["has_mcp_instance"]:
        issues.append("缺少MCP实例创建: mcp = FastMCP('tool_name')")
    
    if not checks["has_mcp_tool_decorator"]:
        issues.append("缺少 @mcp.tool() 装饰器")
    
    if not checks["has_register_tools"]:
        issues.append("缺少 register_tools 函数")
    
    if checks["has_dangerous_operations"]:
        issues.append("包含危险操作，可能导致安全警告")
        suggestions.append("避免使用 os.system、subprocess、eval、exec 等危险操作")
    
    if checks["has_langchain_tool"]:
        issues.append("使用了 Langchain 的 @tool 装饰器，应该使用 @mcp.tool()")
        suggestions.append("将 @tool 替换为 @mcp.tool()")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "suggestions": suggestions,
        "checks": checks
    }


def register_tools(mcp_instance):
    """注册工具到MCP服务器"""
    mcp_instance.add_tool(get_mcp_template, name="get_mcp_template")
    mcp_instance.add_tool(get_common_issues, name="get_common_issues")
    mcp_instance.add_tool(validate_mcp_code, name="validate_mcp_code")


print(f"🐱 MCP模板指导工具 'mcp_template_guide' 加载完成")

