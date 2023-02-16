"""Запрашивает через API самые дешевые отели по запросу пользователя.

Functions:
    get_lowprice_results: Получает самые дешевые предложения по отелям
"""

from typing import List, Tuple

from states.users import Users

from .common import api_request
from .formatted_hotels_info import get_formatted_hotels_info


def get_lowprice_results(user: Users) -> List[Tuple[str, List]]:
    """Получает результаты поиска отелей с самой низкой ценой по запросу пользователя.

    :param user: Объект класса User (содержит все аттрибуты для выполнения запроса)
    :return: Список отелей. Каждый отель представлен кортежем из адреса и списка ссылок на фото отеля
    """
    request_data = {
        "user_id": user.user_id,
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": user.region_id},
        "checkInDate": {
            "day": user.check_in_date.day,
            "month": user.check_in_date.month,
            "year": user.check_in_date.year,
        },
        "checkOutDate": {
            "day": user.check_out_date.day,
            "month": user.check_out_date.month,
            "year": user.check_out_date.year,
        },
        "rooms": [{"adults": 2}],
        "resultsStartingIndex": 0,
        "resultsSize": user.results_size,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {"max": 100000, "min": 1}},
    }
    results = api_request(method_endswith="properties/v2/list", params=request_data, method_type="POST")
    found_hotels = results["data"]["propertySearch"]["properties"]
    return get_formatted_hotels_info(user=user, all_hotels=found_hotels)
