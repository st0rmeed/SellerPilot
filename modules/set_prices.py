import sys
import json

from modules.log import logger
from modules.search_element import search_element
from config import load_paths

try:
    paths = load_paths('paths.json')
    logger.debug('Данные о путях из файла успешно получены')
except Exception as e:
    logger.critical(f'Ошибка вызова функции для получения путей: {e}')
    sys.exit()


def set_prices(driver):
    try:
        with open(paths.user_data.settings, "r", encoding="utf8") as f:
            data = json.load(f)
            price_from_value = data["price_from_value"]
            price_up_to_value = data["price_up_to_value"]
            wait = float(data["wait"])
        logger.debug(
            f"Из settings.json получены настройки: price_from_value={price_from_value}, price_up_to_value={price_up_to_value}"
        )
    except Exception as e:
        logger.error(f"Ошибка применения настроек из settings.json: {str(e)}")
        return False

    try:
        with open(paths.data.locators, "r", encoding="utf8") as f:
            data = json.load(f)
            price_from_locator = tuple(data["price_from_locator"].split("&"))
            price_up_to_locator = tuple(data["price_up_to_locator"].split("&"))
            logger.debug(
                f"Из locators.json получено: price_from_locator={price_from_locator}, price_up_to_locator={price_up_to_locator}"
            )
    except Exception as e:
        logger.error(f"Ошибка получения данных из locators.json: {str(e)}")
        return False

    try:
        price_from_field = search_element(driver, price_from_locator, wait)
        logger.debug('Поле "Цена от" найдено')
    except Exception as e:
        logger.error(f'Ошибка поиска поля ввода значения "Цена от": {str(e)}')
        return False

    try:
        price_from_field.clear()
        price_from_field.send_keys(price_from_value)
        logger.debug('Значение поля "Цена от" изменено')
    except Exception as e:
        logger.error(
            f'Ошибка введения нового значения для поля "Цена от": {str(e)}')
        return False

    try:
        price_up_to_field = search_element(driver, price_up_to_locator, wait)
        logger.debug('Поле "Цена до" найдено')
    except Exception as e:
        logger.error(f'Ошибка поиска поля "Цена до": {str(e)}')
        return False

    try:
        price_up_to_field.clear()
        price_up_to_field.send_keys(price_up_to_value)
        logger.debug('Значение поля "Цена до" изменено')
    except Exception as e:
        logger.error(f'Ошибка изменения значения поля "Цена до": {str(e)}')
        return False

    return True
