"""Форматирует информацию об отелях для вывода пользователю.

Functions:
    get_formatted_hotels_info: Форматирование информации об отелях
"""
from typing import List, Tuple

from database.history.crud import add_result_to_db
from states.users import Users
from utils.logging import logger

from .details import get_details


def get_formatted_hotels_info(user: Users, all_hotels: List) -> List[Tuple[str, List]]:
    """Преобразует полученную информацию об отеле в список для вывода пользователю.

    :param user: Объект класса User, содержащий необходимые аттрибуты для настройки вывода результатов
    :param all_hotels: Все найденные ранее отели
    :return: Список отелей. Каждый отель представлен кортежем из адреса и списка ссылок на фото отеля
    """
    hotels = list()
    db_results = list()
    for i_hotel in range(user.results_size):
        try:
            if user.current_cmd == "/highprice":
                hotel = all_hotels[-i_hotel - 1]
            else:
                hotel = all_hotels[i_hotel]
            photos, address = get_details(hotel["id"], user)

            hotel_info = {
                "db": {
                    "request_id": user.request,
                    "name": f'[{hotel["name"]}](https://www.hotels.com/h{hotel["id"]}.Hotel-Information)',
                    "distance": hotel["destinationInfo"]["distanceFromDestination"]["value"],
                    "price": hotel["price"]["lead"]["formatted"],
                    "total": hotel["price"]["displayMessages"][1]["lineItems"][0]["value"].replace(" total", ""),
                },
                "text": {"address": address, "days": user.total_days, "score": hotel["reviews"]["score"]},
            }

            text = (
                f"{hotel_info['db']['name']}\n"
                f"{hotel_info['text']['address']}\n"
                f"До центра {hotel_info['db']['distance']} миль\n"
                f"Стоимость за одну ночь: {hotel_info['db']['price']}\n"
                f"Ночей: {hotel_info['text']['days']}\n"
                f"Общая стоимость: {hotel_info['db']['total']}\n"
                f"Оценка отеля: {hotel_info['text']['score']}"
            )

            hotels.append((text, photos))
            db_results.append(hotel_info["db"])
        except IndexError:
            logger.info(f"Found {len(hotels)} result of {user.results_size}", user_id=user.user_id)
            break
    add_result_to_db(db_results)
    return hotels
