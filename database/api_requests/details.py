"""Получение от API детальной информации об отеле.

Functions:
    get_details: Получает ссылки на фотографии и адрес
"""

from typing import List, Tuple

from states.users import Users

from .common import api_request


def get_details(property_id: str, user: Users) -> Tuple[List, str]:
    """Получает ссылки на фотографии и адрес.

    :param property_id: id отеля
    :param user: объект класса User, содержащий необходимые для запроса аттрибуты
    :return: Кортеж из списка ссылок на фотографии отеля и адреса
    """
    request_data = {
        "user_id": user.user_id,
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": property_id,
    }
    results = api_request(method_endswith="properties/v2/detail", params=request_data, method_type="POST")
    photos = list()
    for i_photo in range(user.number_of_photos):
        photos.append(results["data"]["propertyInfo"]["propertyGallery"]["images"][i_photo]["image"]["url"])

    address = results["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]
    return photos, address
