from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from time import sleep
import json
import sys

from modules.log import logger
from config import load_paths

try:
    paths = load_paths('paths.json')
    logger.debug('Данные о путях из файла успешно получены')
except Exception as e:
    logger.critical(f'Ошибка вызова функции для получения путей: {e}')
    sys.exit()


def select_combo_value(driver, xpath, desired_value):
    try:
        with open(paths.user_data.settings, "r", encoding="utf8") as f:
            data = json.load(f)
            wait = float(data["wait"])
            micro_wait = float(data["micro_wait"])
            count_scrolls = int(data["count_scrolls"])
            logger.debug(
                f"Из settings.json получено: wait={wait}, micro_wait={micro_wait}, count_scrolls={count_scrolls}"
            )
    except Exception as e:
        logger.error(f"Ошибка получения данных из settings.json: {str(e)}")
        return False

    try:
        with open(paths.data.locators, "r", encoding="utf8") as f:
            data = json.load(f)
            combobox_elements = tuple(data["combobox_elements"].split("&"))
            logger.debug(
                f"Из locators.json получено: combobox_elements={combobox_elements}"
            )
    except Exception as e:
        logger.error(f"Ошибка получения данных из locators.json: {str(e)}")
        return False

    sleep(micro_wait)

    try:
        combobox_element = WebDriverWait(driver, wait).until(
            EC.visibility_of_element_located(("xpath", xpath))
        )
        logger.debug(f"Комбо бокс с {desired_value} найден")
    except Exception as e:
        logger.error(f"Ошибка поиска комбо бокса с {desired_value}: {str(e)}")
        return False

    sleep(micro_wait)

    try:
        combobox_element.clear()
        logger.debug("Комбо бокс очищен")
    except Exception as e:
        logger.error(f"Ошибка очистки комбо бокса: {str(e)}")

    sleep(micro_wait)

    try:
        combobox_element.send_keys(desired_value)
        logger.debug(f"Значение {desired_value} введено")
    except Exception as e:
        logger.error(f"Ошибка ввода значения {desired_value}: {str(e)}")
        return False

    sleep(micro_wait)

    try:
        elements = WebDriverWait(driver, wait).until(
            EC.visibility_of_all_elements_located(
                (
                    "xpath",
                    "//*[contains(@id, 'vaadin-combo-box-item-') and not(@hidden)]",
                )
            )
        )
        logger.debug("Значения выпадающего списка найдены")
    except Exception as e:
        logger.error(
            f"Ошибка поиска доступных элементов комбо бокса: {str(e)}")
        return False

    if len(elements) > 1:
        logger.debug(f"Всего найдено {len(elements)} значений")
        # Прокрутка вверх
        logger.debug("Начат процесс скрола выпадающего списка вверх")
        for i in range(count_scrolls):
            try:
                logger.debug(f"Начата {i} итерация скрола")
                first_items = WebDriverWait(driver, wait).until(EC.visibility_of_all_elements_located(
                    ("xpath", "//*[contains(@id, 'vaadin-combo-box-item-') and not(@hidden)]",)))
                if first_items:
                    logger.debug(
                        f"Найден новый элемент выпадающего списка: {first_items[0].text}"
                    )
                    ActionChains(driver).move_to_element(
                        first_items[0]).perform()
                    logger.debug(
                        f"Выпадающий список прокручен до элемента {first_items[0].text}"
                    )
            except:
                logger.debug("Не найдено новых элементов выпадающего списка")
                break
        logger.debug("Закончен процесс скрола выпадающего списка вверх")

        seen_texts = set()

        logger.debug("Начат процесс скрола выпадающего списка вниз")
        while True:
            try:
                logger.debug(
                    "Начат процесс поиска элементов выпадающего списка")
                items = WebDriverWait(driver, wait).until(
                    EC.visibility_of_all_elements_located(
                        ("xpath",
                         "//*[contains(@id, 'vaadin-combo-box-item-') and not(@hidden)]",)
                    ))
                logger.debug("Найдены элементы выпадающего списка")
            except Exception as e:
                logger.error(
                    f"Ошибка поиска элементов выпадающего списка: {str(e)}")
                return False

            new_found = False

            if not items:
                logger.error(
                    f"Выпадающий список просколен вниз, значение {desired_value} не найдено"
                )
                return False

            logger.debug(
                f"Начат процесс сравнения новых элементов с {desired_value}")
            for item in items:
                text = item.text.strip()
                if text == desired_value:
                    try:
                        logger.debug(
                            f"Значение {desired_value} найдено. Начат скрол к нему, затем выбор его"
                        )
                        ActionChains(driver).move_to_element(item).perform()
                        ActionChains(driver).click(item).perform()
                        logger.debug(
                            f"Выпадающий список просколен к нему. Значение {desired_value} выбрано"
                        )
                    except Exception as e:
                        logger.error(
                            f"Ошибка скрола/выбора значения {desired_value}: {str(e)}"
                        )
                        return False
                    return True

                if text and text not in seen_texts:
                    logger.debug(f"Найдено новое значение: {text}")
                    seen_texts.add(text)
                    new_found = True

            if not new_found:
                logger.error(
                    f"Новых значений, как и нужного {desired_value}, не найдено"
                )
                return False

            try:
                logger.debug(
                    f"Начат процесс перемещения к нижнему из найденых значений ({items[-1].text})"
                )
                ActionChains(driver).move_to_element(items[-1]).perform()
                logger.debug("Перемещение к новому значению выполнено")
            except:
                logger.error(
                    f"Ошибка перемещения к новому значению {items[-1].text}: {str(e)}"
                )
                return False

            sleep(micro_wait)
    else:
        logger.debug("Найдено одно значение")
        try:
            elements[0].click()
            logger.debug(f"Значение {elements[0].text} выбрано")
        except Exception as e:
            logger.error(
                f"Ошибка нажатия на значение {elements[0].text}: {str(e)}")
            return False

    return True
