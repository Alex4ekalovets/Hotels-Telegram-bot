"""Запрашивает через API лучшие отели по запросу пользователя.

Functions:
    get_bestdeal_results: Получает лучшие предложения по отелям
"""

from typing import Any, Dict, List, Tuple

from states.users import Users

from .common import api_request
from .formatted_hotels_info import get_formatted_hotels_info


def get_bestdeal_results(user: Users) -> Tuple[List, bool]:
    """Получает результаты поиска лучшего отеля по цене и расстоянию.

    :param user:
        Объект класса User (содержит все аттрибуты для выполнения запроса)
    :return:
        Кортеж со списком отелей и флагом True, если результаты соответствуют запросу пользователя или False,
    если результаты не соответствуют запрошенному пользователем диапазону расстояний от центра
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
        "filters": {"price": {"max": user.max_price, "min": user.min_price}},
    }

    results = api_request(method_endswith="properties/v2/list", params=request_data, method_type="POST")

    found_hotels = results["data"]["propertySearch"]["properties"]
    filtered_hotels = [
        hotel
        for hotel in found_hotels
        if user.min_distance <= hotel["destinationInfo"]["distanceFromDestination"]["value"] <= user.max_distance
    ]
    if len(filtered_hotels) < user.results_size and len(found_hotels) == 200:
        request_data["filters"]["price"]["min"] = results["data"]["propertySearch"]["filterMetadata"]["priceRange"][
            "max"
        ]
        results = api_request(method_endswith="properties/v2/list", params=request_data, method_type="POST")
        found_hotels = results["data"]["propertySearch"]["properties"]
        add_hotels = [
            hotel
            for hotel in found_hotels
            if hotel["destinationInfo"]["distanceFromDestination"]["value"]
            in range(user.min_distance, user.max_distance)
        ]
        filtered_hotels.append(add_hotels)
    if len(filtered_hotels) > 0:
        return get_formatted_hotels_info(user=user, all_hotels=filtered_hotels), True
    return get_formatted_hotels_info(user=user, all_hotels=found_hotels), False
