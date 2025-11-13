from langchain.tools import tool
from ..core import config


def _get_current_path_impl() -> str:
    """
    获取当前项目根目录路径的原始实现函数

    Returns:
        str: 当前项目根目录的绝对路径
    """
    return config.PROJECT_ROOT


@tool
def get_current_path() -> str:
    """
    【权限说明】信息查询 - 了解环境

    🐱 猫猫权限：查看项目位置

    ✅ 功能：
    - 返回项目根目录的绝对路径
    - 帮助猫猫了解自己的活动范围

    ❌ 限制：
    - 不能改变当前目录
    - 不能越权访问其他目录

    Returns:
        str: 项目根目录的绝对路径
    """
    return _get_current_path_impl()