"""Получение от API списка городов схожих с запросом пользователя.

Functions:
    find_city: Поиск городов по запросу пользователя
"""

from typing import Dict, List

from states.users import Users
from utils.logging import logger

from .common import api_request


def find_city(user: Users) -> List[Dict]:
    """Получает результаты поиска города по запросу пользователя.

    :param user:
        Объект класса User (содержит все аттрибуты для выполнения запроса).
    :return:
        Список городов. Каждый город представлен словарем с ключами "name" - название и "id".
    """
    request_data = {
        "user_id": user.user_id,
        "q": user.city,
        "locale": "en_US",
        "langid": "1033",
        "siteid": "300000001",
    }
    results = api_request(method_endswith="locations/v3/search", params=request_data, method_type="GET")
    cities = list()
    try:
        for result in results["sr"]:
            if result["type"] == "CITY":
                cities.append({"name": result["regionNames"]["displayName"], "id": result["gaiaId"]})
    except Exception as exc:
        logger.error(f"find_city {exc}", user_id=user.user_id)
    return cities
