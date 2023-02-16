"""Запрашивает через API самые дорогие отели по запросу пользователя.

Functions:
    get_highprice_results: Получает самые дорогие предложения по отелям
"""

from typing import Any, Dict, List, Tuple

from states.users import Users

from .common import api_request
from .formatted_hotels_info import get_formatted_hotels_info


def get_highprice_results(user: Users) -> List[Tuple[str, List]]:
    """Получает результаты поиска отеля с самой высокой ценой по запросу пользователя.

    :param user: Объект класса User (содержит все аттрибуты для выполнения запроса)
    :return: Список отелей. Каждый отель представлен кортежем из адреса и списка ссылок на фото отеля
    """
    request_data: Dict[str, Any] = {
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
        "resultsSize": 200,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {"max": 100000, "min": 301}},
    }
    results = api_request(method_endswith="properties/v2/list", params=request_data, method_type="POST")

    try:
        found_hotels = results["data"]["propertySearch"]["properties"]
    except TypeError:
        request_data["filters"]["price"]["min"] = 1
        results = api_request(method_endswith="properties/v2/list", params=request_data, method_type="POST")
        found_hotels = results["data"]["propertySearch"]["properties"]
    while len(found_hotels) == 200:
        last_ten_hotels = found_hotels[189:]
        request_data["filters"]["price"]["min"] = results["data"]["propertySearch"]["filterMetadata"]["priceRange"][
            "max"
        ]
        results = api_request(method_endswith="properties/v2/list", params=request_data, method_type="POST")
        found_hotels = results["data"]["propertySearch"]["properties"]
        if len(found_hotels) < user.results_size:
            found_hotels = last_ten_hotels + found_hotels

    return get_formatted_hotels_info(user=user, all_hotels=found_hotels)
