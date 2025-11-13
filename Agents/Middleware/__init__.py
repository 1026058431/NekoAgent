# 🐱 Agents.Middleware 中间件包
# 包含各种Agent中间件的实现

"""
Agents.Middleware 中间件包

这个包包含了NekoAgent使用的各种中间件：
- AgentSummarizationMiddleware: 智能总结中间件
- SimpleApprovalMiddleware: 简单审批中间件

使用说明：
1. 导入方式：from Agents.Middleware import AgentSummarizationMiddleware, SimpleApprovalMiddleware
2. 或者：from Agents.Middleware.Agent_Summarization import AgentSummarizationMiddleware
3. 主要用于Agent.py内部使用

注意：这个包是Agent.py的内部组件，不建议直接从外部导入使用。
"""

__version__ = "1.0.0"
__author__ = "Neko"

# 定义包的公开接口
__all__ = [
    "AgentSummarizationMiddleware",
    "SimpleApprovalMiddleware"
]

# 导入主要中间件类，方便直接使用 from Agents.Middleware import AgentSummarizationMiddleware
from .Agent_Summarization import AgentSummarizationMiddleware
from .SimpleApprovalMiddleware import SimpleApprovalMiddleware

# 包级别初始化（可选）
print("🐱 Agents.Middleware 中间件包已加载")