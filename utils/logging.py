"""Модуль настройки loguru."""

import json
import sys
from typing import Any, Dict

from loguru import logger


def serialize(record: Dict) -> str:
    """Сериализация сообщения loguru.

    :param record: Сообщение loguru
    :return: Сериализованное сообщение
    """
    subset = {
        "user_id": record["extra"]["user_id"],
        "timestamp": record["time"].timestamp(),
        "message": record["message"],
        "level": record["level"].name,
    }
    return json.dumps(subset)


def patching(record: Any) -> None:
    """Изменение вывода сообщений loguru."""
    record["extra"]["serialized"] = serialize(record)


logger.remove(0)
logger = logger.patch(patching)
logger.add("logs/logs_{time}.json", format="{extra[serialized]}", rotation="1 hour")
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "| <yellow>User: {extra[user_id]}</yellow> | "
    "<level>{message}</level>",
)
