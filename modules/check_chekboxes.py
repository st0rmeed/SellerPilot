from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.log import logger
from config import load_paths

import json
import sys

try:
    paths = load_paths('paths.json')
    logger.debug('Данные о путях из файла успешно получены')
except Exception as e:
    logger.critical(f'Ошибка вызова функции для получения путей: {e}')
    sys.exit()


# поиск чекбокса является поэтапным, а не в один Xpath, в связи с тем, что
# selenium не способен работать с такими сложными Xpath'ами, он выдает ошибку
# поиска без указания сообщения


def check_checkboxes(driver, wait):
    try:
        with open(paths.user_data.settings, "r", encoding="utf8") as f:
            data = json.load(f)
            texts = data["texts"].split(";")
            wait = float(data["wait"])
            logger.debug(
                f"Данные из settings.json получены: texts={texts}, wait={wait}"
            )
    except Exception as e:
        logger.error(f"Ошибка получения данных из settings.json: {str(e)}")
        return False

    for label_text in texts:
        # находим лейбл по тексту
        try:
            label = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located(
                    ("xpath", f"//label[normalize-space()='{label_text}']")
                )
            )
            logger.debug(f"Лейбл {label_text}, связанный с чекбоксом найден")
        except Exception as e:
            logger.error(
                f"Не удалось найти чекбокс с текстом {label_text}: {str(e)}")
            return False

        # получаем id связанного чекбокса
        try:
            checkbox_id = label.get_attribute("for")
            logger.debug("Id связанного чекбокса получено")
        except Exception as e:
            logger.error(
                f"Не удалось получить id свящанного чекбокса {label_text}: {str(e)}"
            )
            return False

        # находим чекбокс по id
        try:
            checkbox = driver.find_element("id", checkbox_id)
            logger.debug("Чекбокс по id найден")
        except Exception as e:
            logger.error(
                f"Не удалось найти чекбокс {label_text} с id {checkbox_id}: {str(e)}"
            )
            return False

        # кликаем если не выбран
        if not checkbox.is_selected():
            try:
                checkbox.click()
                logger.debug(f"Чекбокс {label_text} выбран")
            except Exception as e:
                logger.error(
                    f"Ошибка нажатия на чекбокс {label_text}: {str(e)}")
                return False
    return True
