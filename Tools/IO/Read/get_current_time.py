from datetime import datetime
from langchain.tools import tool


def _get_current_time_impl() -> str:
    """
    获取当前时间的原始实现函数

    Returns:
        str: 当前时间的字符串表示，格式：YYYY-MM-DD HH:MM:SS
    """
    # 获取当前时间
    current_time = datetime.now()

    # 格式化为字符串
    time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    return time_str


@tool
def get_current_time() -> str:
    """
    【功能说明】时间查询 - 获取当前时间

    🐱 猫猫权限：查看当前时间

    ✅ 功能：
    - 返回当前系统时间的字符串表示
    - 包含日期和时间信息
    - 格式：YYYY-MM-DD HH:MM:SS

    ❌ 限制：
    - 只能获取时间，不能修改系统时间
    - 返回的是字符串格式，不能直接用于时间计算

    Returns:
        str: 当前时间的字符串表示，格式：YYYY-MM-DD HH:MM:SS
    """
    return _get_current_time_impl()