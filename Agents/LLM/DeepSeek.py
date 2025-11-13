from langchain_deepseek import ChatDeepSeek
import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment_variables():
    """从项目根目录加载 .env 文件"""
    # 获取当前文件的绝对路径
    current_file = Path(__file__).resolve()

    # 向上导航到项目根目录（假设 .env 在项目根目录）
    project_root = current_file.parent.parent.parent

    # 构建 .env 文件的完整路径
    env_path = project_root / '.env'

    # 加载环境变量
    load_dotenv(env_path)

    # 验证是否加载成功
    if not os.getenv('DEEPSEEK_API_KEY'):
        raise FileNotFoundError(f"无法在 {env_path} 找到 .env 文件或 DEEPSEEK_API_KEY 未设置")

# 在程序开始时调用
load_environment_variables()

# 现在可以安全地使用环境变量
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# print(f"API 密钥已加载: {DEEPSEEK_API_KEY[:5]}...")

DEEPSEEK = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.06,
    max_tokens=None,
    timeout=10,
    max_retries=2,
    api_key=DEEPSEEK_API_KEY
    # other params...
)
