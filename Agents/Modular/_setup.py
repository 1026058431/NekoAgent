# log_config.py
"""
猫娘专用日志配置模块
作者：Neko 猫娘
"""

import logging
from logging.handlers import RotatingFileHandler
import pathlib
from typing import Optional


def setup_logging(
    log_dir: Optional[str | pathlib.Path] = None,
    log_name: str = "agent.log",
    level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,   # 5 MB
    backup_count: int = 3,
    encoding: str = "utf-8",
) -> None:
    """
    初始化日志系统，使用 RotatingFileHandler 自动切分文件。

    参数：
        log_dir      : 日志所在目录，默认与此文件同目录
        log_name     : 日志文件名
        level        : 日志级别
        max_bytes    : 单文件最大字节数
        backup_count : 备份文件数量
        encoding     : 文件编码
    """
    if log_dir is None:
        log_dir = pathlib.Path(__file__).parent
    else:
        log_dir = pathlib.Path(log_dir)

    log_file = log_dir / log_name

    # 创建 RotatingFileHandler
    handler = RotatingFileHandler(
        filename=str(log_file),
        mode="a",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=encoding,
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # 获取根 logger（或自定义名字）
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()          # 清除已有 handler，避免重复
    logger.addHandler(handler)

    # 兼容旧的 `logging.basicConfig` 用法
    logging.basicConfig(
        handlers=[handler],
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding=encoding,
        filemode="a",
    )