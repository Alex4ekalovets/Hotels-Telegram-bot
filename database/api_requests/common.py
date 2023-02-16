"""Запросы к API сайта с отелями Hotels.com.

Functions:
    try_request: декоратор для повторных попыток подключения
    api_request: функция для запросов к API с методами POST и GET
    get_request: GET запросы
    post_request: POST запросы
"""

import functools
import json
from time import sleep
from typing import Any, Callable, Dict, Optional

from requests import exceptions, get, post

from config_data.config import RAPID_API_KEY
from utils.logging import logger


def try_request(func: Callable) -> Callable:
    """Декоратор, для повторных попыток запроса на сервер."""

    @functools.wraps(func)
    def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        delay = 0.2
        factor = 3
        last_exc: Optional[ConnectionError] = None

        for attempt in range(1, 4):
            try:
                return func(*args, **kwargs)
            except ConnectionError as exc:
                last_exc = exc
                logger.error(
                    f'Try {attempt}, delay {delay} sec, {func.__name__}, {kwargs["url"]}',
                    user_id=kwargs["params"]["user_id"],
                )
                sleep(delay)
                delay = delay * factor
        raise ConnectionError(f"Request {last_exc}")

    return wrapped_func


def api_request(
    method_endswith: str, params: Dict, method_type: str, good_status: int = 200, timeout: int = 15
) -> Dict:
    """Универсальная функция для запросов к API с методами POST и GET.

    :param timeout:
    :param good_status:
    :param method_endswith: окончание ссылки на endpoint
    :param params: параметры запроса
    :param method_type: Метод запроса - POST или GET
    :return: Ответ на POST или GET запрос
    """
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"
    if method_type == "GET":
        return get_request(url=url, params=params, status=good_status, timeout=timeout)
    return post_request(url=url, params=params, status=good_status, timeout=timeout)


@try_request
def get_request(url: str, params: Dict, status: int, timeout: int) -> Optional[Dict]:
    """Получает ответ на GET запрос.

    :param timeout:
    :param status:
    :param url: ссылка на endpoint
    :param params: параметры запроса
    :return: Ответ на GET запрос
    :except ConnectionError: Возвращает исключение, если статус ответа сервера не равен 200
    или превышено время ожидания ответа от сервера
    """
    try:
        response = get(
            url,
            headers={"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "hotels4.p.rapidapi.com"},
            params=params,
            timeout=timeout,
        )
        if response.status_code == status:
            logger.success(f"GET Request {url} OK", user_id=params["user_id"])
            return json.loads(response.text)
        raise ConnectionError(f"GET Request url {url} response code {response.status_code}")
    except exceptions.ReadTimeout as exc:
        raise ConnectionError(f"GET Request url {url} {exc}")


@try_request
def post_request(url: str, params: Dict, status: int, timeout: int) -> Optional[Dict]:
    """Получает ответ на POST запрос.

    :param timeout:
    :param status:
    :param url: ссылка на endpoint
    :param params: параметры запроса
    :return: Ответ на GET запрос
    :except ConnectionError: Возвращает исключение, если статус ответа сервера не равен 200
    или превышено время ожидания ответа от сервера
    """
    try:
        response = post(
            url,
            headers={
                "content-type": "application/json",
                "X-RapidAPI-Key": RAPID_API_KEY,
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
            },
            json=params,
            timeout=timeout,
        )
        if response.status_code == status:
            logger.success(f"POST Request {url} OK", user_id=params["user_id"])
            return json.loads(response.text)
        raise ConnectionError(f"POST Request url {url} response code {response.status_code}")
    except exceptions.ReadTimeout as exc:
        raise ConnectionError(f"POST Request url {url} {exc}")
