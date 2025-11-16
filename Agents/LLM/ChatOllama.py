import os
from pathlib import Path
from langchain_ollama import ChatOllama

# 加载.env文件 - 从项目根目录
from dotenv import load_dotenv

# 获取项目根目录路径
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"

# 加载.env文件
load_dotenv(env_path)

# 从环境变量获取Ollama基础URL，默认为localhost:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def create_ollama_client(model_config: dict):
    """创建Ollama客户端"""
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        **model_config
    )

GPT_OSS = create_ollama_client({
    "model": "gpt-oss:20b",
    "reasoning": "low",
    "temperature": 0.666,
    "num_ctx": 65530,
    "num_predict": 4096,
})

QWEN3_MINI = create_ollama_client({
    "model": "qwen3",
    "reasoning": "true",
    "temperature": 0.666,
    "num_ctx": 8192,
    "num_predict": 4096,
})

QWEN3 = create_ollama_client({
    "model": "qwen3:30b",
    "reasoning": "false",
    "temperature": 0.666,
    "num_ctx": 65530,
    "num_predict": 4096,
})