"""Модуль взаимодействия с базой данных истории запросов.

Functions:
    try_open_db: Декоратор для попыток подключения к БД
    add_result_to_db: Добавить результаты поиска в БД
    add_request_to_db: Добавить запрос пользователя в БД
    get_requests_from_db: Получить запросы пользователя из БД
    get_results_from_db:  Получить результаты поиск по запросу пользователя из БД
"""
import functools
from collections.abc import Callable
from time import sleep
from typing import Any, Dict, List, Optional

import peewee

from states.users import Users
from utils.logging import logger

from .model import Request, Result, User, db


def try_open_db(func: Callable) -> Callable:
    """Декоратор, для повторных попыток доступа к базе данных и логирования."""

    @functools.wraps(func)
    def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        if isinstance(args[0], Users):
            user_id = args[0].user_id
        elif isinstance(args[0], int):
            user_id = args[0]
        else:
            user_id = args[0][0]["request_id"].user.user_id
        while True:
            try:
                result = func(*args, **kwargs)
                logger.success(f"{func.__name__} completed successfully", user_id=user_id)
                return result
            except peewee.OperationalError as exc:
                logger.debug(f"{func.__name__} {exc}", user_id=user_id)
                sleep(0.1)

    return wrapped_func


@try_open_db
def add_result_to_db(results: List[Dict]) -> None:
    """Добавляет результаты поиска в базу данных.

    :param results: Список результатов поиска. Каждый результат - словарь
    """
    with db.atomic():
        Result.insert_many(results).execute()


@try_open_db
def add_request_to_db(user: Users) -> None:
    """Добавляет запрос пользователя в базу данных. Удаляет самый старый запрос, если количество записей превышает 10.

    :param user: Объект класса User, атрибуты которого содержат полную информацию о запросе
    """
    with db.atomic():
        user_db = User.get_or_create(user_id=user.user_id)
        user_requests = Request.select().join(User).order_by(Request.created_time).where(User.user_id == user.user_id)

        if user_requests.count() >= 10:
            user_requests[0].delete_instance()
        user.request = Request.create(
            user=user_db[0],
            command=user.current_cmd,
            created_time=user.creation_instance_time,
            region_id=user.region_id,
            city=user.city,
            results_size=user.results_size,
            number_of_photos=user.number_of_photos,
            min_price=user.min_price,
            max_price=user.max_price,
            check_in_date=user.check_in_date,
            check_out_date=user.check_out_date,
            min_distance=user.min_distance,
            max_distance=user.max_distance,
        )


@try_open_db
def get_requests_from_db(user_id: int, request_id: Optional[int] = None) -> peewee.ModelSelect:
    """Получает один определенный или все запросы пользователя из базы данных.

    :param user_id: Telegram id пользователя
    :param request_id: Номер единичного запроса, который нужно вернуть. Если None - возвращаются все запросы
    :return: объект ModelSelect с одним или всеми запросами пользователя
    """
    with db.atomic():
        if request_id:
            requests = Request.select().where(Request.id == request_id).limit(1)
        else:
            requests = Request.select().join(User).where(User.user_id == user_id)
    return requests


@try_open_db
def get_results_from_db(user_id: int, request_id: int) -> peewee.ModelSelect:
    """Получает все результаты поиска по данному запросу пользователя.

    :param user_id: Telegram id пользователя
    :param request_id: Номер запроса, для которого возвращаются результаты поиска
    :return: объект ModelSelect с результатами поиска по указанному запросу
    """
    with db.atomic():
        results = Result.select().where(Result.request_id == request_id)
    return results
