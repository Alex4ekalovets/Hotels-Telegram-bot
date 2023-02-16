"""Модуль состояний бота."""
from telebot.handler_backends import State, StatesGroup


class UserSearchState(StatesGroup):
    """Класс состояний поиска пользователя.

    Attributes:
        city: Состояние, при котором ожидается ввод города пользователем в запросе
        verified_city: Состояние, при котором ожидается выбор города пользователем из предложенных
        number_of_hotels: Состояние, при котором ожидается выбор или ввод количества отелей
        number_of_photo: Состояние, при котором ожидается выбор количества фотографий
        min_price: Состояние, при котором ожидается ввод минимальной стоимости за ночь
        max_price: Состояние, при котором ожидается ввод максимальной стоимости за ночь
        min_distance: Состояние, при котором ожидается ввод минимальной дистанции
        max_distance: Состояние, при котором ожидается ввод максимальной дистанции
        checkin_date: Состояние, при котором ожидается выбор даты заезда
        checkout_date: Состояние, при котором ожидается выбор даты выезда
        check_date: Состояние, при котором ожидается подтверждение выбранной даты
        history_request_action: Состояние, при котором ожидается выбор действия с запросом из истории
        game_name: Состояние, при котором ожидается ввод игрового имени
        game_cities: Состояние, при котором ожидается выбор пункта игрового меню
        game_cities_start: Состояние, при котором начинается игра
        game_change_name: Состояние, при котором ожидается изменение игрового имени
        get_password: Состояние, при котором ожидается ввод пароля
        choice_db: Состояние, при котором ожидается выбор базы данных для очистки
    """

    city = State()
    verified_city = State()
    number_of_hotels = State()
    number_of_photo = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    checkin_date = State()
    checkout_date = State()
    check_date = State()
    history_request_action = State()
    game_name = State()
    game_cities = State()
    game_cities_start = State()
    game_change_name = State()
    get_password = State()
    choice_db = State()
