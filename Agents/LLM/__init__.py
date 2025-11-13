# 🐱 Agents.LLM 语言模型包
# 包含各种LLM模型的实现

"""
Agents.LLM 语言模型包

这个包包含了NekoAgent支持的各种语言模型：
- DeepSeek: DeepSeek API模型
- ChatOllama: 本地Ollama模型

使用说明：
1. 导入方式：from Agents.LLM import DEEPSEEK, GPT_OSS, QWEN3, QWEN3_MINI
2. 或者：from Agents.LLM.DeepSeek import DEEPSEEK
3. 主要用于Agent.py内部使用

注意：这个包是Agent.py的内部组件，不建议直接从外部导入使用。
"""

__version__ = "1.0.0"
__author__ = "Neko"

# 定义包的公开接口
__all__ = [
    "DEEPSEEK",
    "GPT_OSS", 
    "QWEN3",
    "QWEN3_MINI"
]

# 导入主要模型实例，方便直接使用 from Agents.LLM import DEEPSEEK
from .DeepSeek import DEEPSEEK
from .ChatOllama import GPT_OSS, QWEN3, QWEN3_MINI

# 包级别初始化（可选）
print("🐱 Agents.LLM 语言模型包已加载")