from Tools.IO.Read import read_file, list_dir_tree, get_current_path, get_current_time
from Tools.IO.Write import write_file, move_file, delete_file, cleanup_empty_directories, cleanup_playground
from Tools.Web.http_client_v4 import get_http
from Tools.Web.send_payloads import send_payloads
from Tools.Report.report_tools import get_report_template, list_all_templates, add_new_template
from Tools.RAG.tools.rag_tools import rag_search, rag_query, rag_system_info, rag_refresh
from Tools.MCP.mcp_client_http import connect_mcp_server, list_mcp_tools, call_mcp_tool, get_mcp_server_info
from Tools.MCP.MCPToolsManager import create_mcp_tool, delete_mcp_tool, list_mcp_tools_local, get_mcp_tools_path_info, scan_mcp_tool_security

# IO工具 - 使用新的模块结构
read_tools = [get_current_time, get_current_path, list_dir_tree, read_file]
write_tools = [write_file, move_file, delete_file, cleanup_empty_directories, cleanup_playground,]

io_tools = read_tools + write_tools

# 网页处理工具
web_tools = [get_http, send_payloads]

# 报告工具
report_tools = [get_report_template, list_all_templates, add_new_template]

# RAG工具
rag_tools = [rag_search, rag_query, rag_system_info, rag_refresh]

# MCP_Client工具
mcp_client_tools = [connect_mcp_server, list_mcp_tools, call_mcp_tool, get_mcp_server_info]

# MCP_Tools管理工具
mcp_tools_manager_tools = [create_mcp_tool, delete_mcp_tool, get_mcp_tools_path_info, scan_mcp_tool_security]

# ⚠️ 注意：本地文件的list_mcp_tools_local和list_mcp_tools功能部分重合，可能让llm感到困惑
mcp_tools_manager_tools += [list_mcp_tools_local]

# 所有工具集合
agent_tools = io_tools + web_tools + report_tools + rag_tools + mcp_client_tools + mcp_tools_manager_tools