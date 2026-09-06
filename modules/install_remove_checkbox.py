from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.log import logger
from config import load_paths

import json
from time import sleep
import sys



try:
    paths = load_paths('paths.json')
    logger.debug('Данные о путях из файла успешно получены')
except Exception as e:
    logger.critical(f'Ошибка вызова функции для получения путей: {e}')
    sys.exit()



def install_remove_checkbox(driver, wait):
    try:
        with open(paths.user_data.settings, "r", encoding="utf8") as f:
            data = json.load(f)
            checkbox_for_update = data["checkbox_for_update"]
            nano_wait = float(data["nano_wait"])
        logger.debug(
            f"Из settings.json получено: checkbox_for_update={checkbox_for_update}, nano_wait={nano_wait}"
        )
    except Exception as e:
        logger.error("Ошибка получения данных из settings.json")
        return False

    # находим лейбл по тексту
    try:
        label = WebDriverWait(driver, wait).until(
            EC.visibility_of_element_located(
                ("xpath",
                 f"//label[normalize-space()='{checkbox_for_update}']")
            )
        )
        logger.debug(
            f"Лейбл, связанный с чекбоксом {checkbox_for_update} найден")
    except Exception as e:
        logger.error(
            f"Не удалось найти чекбокс с текстом {checkbox_for_update}: {str(e)}"
        )
        return False

    # получаем id связанного чекбокса
    try:
        checkbox_id = label.get_attribute("for")
        logger.debug("Получен id связанного чекбокса")
    except Exception as e:
        logger.error(
            f"Не удалось получить id связанного чекбокса {checkbox_for_update}: {str(e)}"
        )
        return False

    # находим сам чекбокс по ID
    try:
        checkbox = driver.find_element("id", checkbox_id)
        logger.debug("Чекбокс по id найден")
    except Exception as e:
        logger.error(
            f"Не удалось найти чекбокс {checkbox_for_update} с id {checkbox_id}: {str(e)}"
        )
        return False

    # нажимаем на чекбокса
    try:
        checkbox.click()
        logger.debug(f"Чекбокс {checkbox_for_update} выбран")
    except Exception as e:
        logger.error(
            f"Ошибка нажатия на чекбокс {checkbox_for_update}: {str(e)}")
        return False

    sleep(nano_wait)

    # отжимаем чекбокс
    try:
        checkbox.click()
        logger.debug(f"Чекбокс {checkbox_for_update} снят")
    except Exception as e:
        logger.error(f"Ошибка снятия чекбокса {checkbox_for_update}: {str(e)}")
        return False

    return True
