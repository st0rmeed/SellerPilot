from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
import json
import sys

from modules.log import logger
from modules.search_element import search_element
from config import load_paths

try:
    paths = load_paths('paths.json')
    logger.debug('Данные о путях из файла успешно получены')
except Exception as e:
    logger.critical(f'Ошибка вызова функции для получения путей: {e}')
    sys.exit()


def looping_imports(field, value, count_attempts, nano_wait):
    logger.debug(
        f"Начат процесс отправки значения {value} ({count_attempts} попыток с инетрвалом {nano_wait})"
    )
    for j in range(count_attempts):
        try:
            logger.debug(f"Начата {j} итерация повторной отправки значения")
            sleep(nano_wait)
            field.send_keys(value)
            logger.debug(f"Успех! С {j} попытки значение {value} отправлено")
            return True
        except Exception as e:
            logger.debug(f"На {j} итерации найдена ошибка: {str(e)}")
            continue
    else:
        logger.error(
            f"Не удалось отправить значение {value} с {count_attempts} попыток с ожиданием {nano_wait} сек"
        )
        return False


def import_product(driver, wait, micro_wait, article):
    try:
        with open(paths.user_data.settings, "r", encoding="utf8") as f:
            data = json.load(f)
            price_multiplier = float(data["price_multiplier"])
            discount = data["discount"]
            duplicates = data["duplicates"]
            price_step = data["price_step"]
            default_weight = data["default_weight"]
            default_size = data["default_size"]
            nano_wait = float(data["nano_wait"])
            count_attempts = int(data["count_attempts"])
            logger.debug(
                f"Из settings.json получено: price_multiplier={price_multiplier}, discount={discount}, duplicates={duplicates}, price_step={price_step}, default_weight={default_weight}, default_size={default_size}, nano_wait={nano_wait}, count_attempts={count_attempts}"
            )
    except Exception as e:
        logger.error(f"Ошибка получения настроек из settings.json: {str(e)}")
        return False

    try:
        with open(paths.data.locators, "r", encoding="utf8") as f:
            data = json.load(f)
            discount_locator = tuple(data["discount_locator"].split("&"))
            price_element_locator = tuple(
                data["price_element_locator"].split("&"))
            price_field_locator = tuple(data["price_field_locator"].split("&"))
            trigger_price_locator = tuple(
                data["trigger_price_locator"].split("&"))
            duplicates_locator = tuple(data["duplicates_locator"].split("&"))
            warehouse_field_locator = tuple(
                data["warehouse_field_locator"].split("&"))
            article_locator = tuple(data["article_locator"].split("&"))
            price_step_locator = tuple(data["price_step_locator"].split("&"))
            brands_locator = tuple(data["brands_locator"].split("&"))
            import_product_button_locator = tuple(
                data["import_product_button_locator"].split("&")
            )
            error_message_locator = tuple(
                data["error_message_locator"].split("&"))
            help_button_locator = tuple(data["help_button_locator"].split("&"))
            cross_button_locator = tuple(
                data["cross_button_locator"].split("&"))

            logger.debug(
                f"Из locators.json получено: discount_locator={discount_locator}, price_element_locator={price_element_locator}, price_field_locator={price_field_locator}, trigger_price_locator={trigger_price_locator}, duplicates_locator={duplicates_locator}, warehouse_field_locator={warehouse_field_locator}, article_locator={article_locator}, price_step_locator={price_step_locator}, brands_locator={brands_locator}, import_product_button_locator={import_product_button_locator}, error_message_locator={error_message_locator}, help_button_locator={help_button_locator}, cross_button_locator={cross_button_locator}"
            )
    except Exception as e:
        logger.error(f"Ошибка загрузки локаторов из locators.json: {str(e)}")
        return False

    # ожидание для предотвращения багов
    sleep(micro_wait)

    # ввод скидки
    try:
        discount_field = search_element(driver, discount_locator, wait)
        logger.debug("Поле ввода скидки найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля ввода скидки: {str(e)}")
        return False

    try:
        discount_field.clear()
        discount_field.send_keys(discount)
        logger.debug("Значение скидки введено")
    except Exception as e:
        logger.error("Ошибка ввода скидки")
        if not looping_imports(discount_field, discount, count_attempts, nano_wait):
            return False

    # получение значения цены
    try:
        price_element = search_element(
            driver, price_element_locator, wait, clickable=False
        )
        logger.debug("Найден элемент, содержащий значение цены")
    except Exception as e:
        logger.error(
            f"Ошибка поиска элемента, содержащего значение цены: {str(e)}")
        return False

    try:
        price = float(
            price_element.get_attribute("textContent")
            .split(":")[1]
            .strip()
            .replace(" руб.", "")
        )
        logger.debug('Значение цены выделено из поля "Цена поставщика"')
    except Exception as e:
        logger.error(
            f'Ошибка выделения значения цены из поля "Цена поставщика": {str(e)}'
        )
        return False

    # ввод цены
    try:
        price_field = search_element(driver, price_field_locator, wait)
        logger.debug("Поле ввода цены найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля ввода цены: {str(e)}")
        return False

    try:
        price_field.clear()
        price_field.send_keys(f"{int(price * price_multiplier)}")

        logger.debug("Значение цены изменено")
    except Exception as e:
        logger.error(f"Ошибка отправки нового значения цены: {str(e)}")
        if not looping_imports(
                price_field, f"{int(price * price_multiplier)}", count_attempts, nano_wait
        ):
            return False

    # ввод триггерной цены
    try:
        trigger_price_field = search_element(
            driver, trigger_price_locator, wait)
        logger.debug("Значение триггерной цены изменено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля ввода триггерной цены: {str(e)}")
        return False

    try:
        trigger_price_field.clear()
        trigger_price_field.send_keys(
            int(((price * 3) - (price * 3 * int(discount)) / 100) * 0.8)
        )

        logger.debug("Новое значение триггерной цены отправлено")
    except Exception as e:
        logger.error(
            f"Ошибка отправки нового значения триггерной цены: {str(e)}")
        if not looping_imports(
                trigger_price_field,
                int(((price * 3) - (price * 3 * int(discount)) / 100) * 0.8),
                count_attempts,
                nano_wait,
        ):
            return False

    # ввод количества дубликатов
    try:
        duplicates_field = search_element(driver, duplicates_locator, wait)
        logger.debug("Поле ввода количества дубликатов найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля ввода дубликатов: {str(e)}")
        return False

    try:
        duplicates_field.clear()
        duplicates_field.send_keys(duplicates)

        logger.debug("Новое значение количества дубликатов отправлено")
    except Exception as e:
        logger.error(
            f"Ошибка отправки нового значения кол-ва дубликатов: {str(e)}")
        if not looping_imports(duplicates_field, duplicates, count_attempts, nano_wait):
            return False

    # получение значения склада
    warehouses_dict = {"EKB": "ЕКБ", "MSK": "МСК", "SPB": "СПБ"}

    # поиск элемента, содержащего склад
    try:
        warehouse_field = search_element(
            driver, warehouse_field_locator, wait, clickable=False
        )
        logger.debug("Поле со складом найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля со складом: {str(e)}")
        return False

    # выделение значения склада
    try:
        warehouse = warehouse_field.text.split("[")[1].split("]")[0]
        logger.debug("Значение склада выделено")
    except Exception as e:
        logger.error(f"Ошибка выделения значения склада: {str(e)}")
        return False

    # поиск поля ввода артикула
    try:
        article_field = search_element(driver, article_locator, wait)
        logger.debug("Поле ввода артикула найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля введения артикула: {str(e)}")
        return False

    # изменение значения артикула
    try:
        article_field.send_keys(f"{warehouses_dict[warehouse]}{int(price)}")
        logger.debug("Значение артикула изменено")
    except Exception as e:
        logger.error(f"Ошибка отправки нового значения артикула: {str(e)}")
        if not looping_imports(
                article_field,
                f"{warehouses_dict[warehouse]}{int(price)}",
                count_attempts,
                nano_wait,
        ):
            return False

    sleep(micro_wait)

    # поле ввода шага цены
    try:
        price_step_field = search_element(driver, price_step_locator, wait)
        logger.debug("Поле ввода шага цены найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля ввода шага цены: {str(e)}")
        return False

    # проверка шага цены
    try:
        if price_step_field.get_attribute("value") != price_step:
            price_step_field.clear()
            sleep(micro_wait)
            price_step_field.send_keys(price_step)
            logger.debug("Значение шага цены изменено")

        else:
            logger.debug("Значение шага цены корректно")
    except Exception as e:
        logger.error(f"Ошибка изменения шага цены: {str(e)}")
        if not looping_imports(price_step_field, duplicates, count_attempts, nano_wait):
            return False

    # проверка габаритов
    parametrs = ["Длина", "Ширина", "Высота", "Вес"]
    for parametr in parametrs:
        try:
            field = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located(
                    (
                        "xpath",
                        f"//input[@id=//label[contains(text(), '{parametr}')]/@for]",
                    )
                )
            )
            logger.debug(f"Поле {parametr.lower()} найдено")
        except Exception as e:
            logger.error(
                f"Ошибка поиска поля ввода {parametr.lower()}: {str(e)}")
            return False

        if float(field.get_attribute("value")) <= 0.1 and parametr == "Вес":
            try:
                field.clear()
                sleep(micro_wait)
                field.send_keys(default_weight)

                logger.debug("Значение веса изменено")
            except Exception as e:
                logger.error(f"Ошибка изменения веса: {str(e)}")
                if not looping_imports(
                        field, default_weight, count_attempts, nano_wait
                ):
                    return False

        elif field.get_attribute("value") == "0":
            try:
                field.clear()
                sleep(micro_wait)
                field.send_keys(default_size)

                logger.debug(f"Значение {parametr.lower()} изменено")
            except Exception as e:
                logger.error(
                    f"Ошибка изменения значения {parametr.lower()}: {str(e)}")
                if not looping_imports(field, default_size, count_attempts, nano_wait):
                    return False

    sleep(micro_wait)

    # поиск поля ввода бренда
    try:
        brands_field = search_element(driver, brands_locator, wait)
        logger.debug("Поле ввода бренда найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля ввода бренда: {str(e)}")
        return False

    # скролл к полю ввода бренда
    try:
        driver.execute_script(
            """
            const element = arguments[0];
            element.scrollIntoView({behavior: 'smooth', block: 'center'});
            window.scrollBy(0, -100);  // Подвинуть чуть выше, если что-то перекрывает
        """,
            brands_field,
        )
        logger.debug("Скрол к полю ввода бренда выполнен")
    except Exception as e:
        logger.error(f"Ошибка скрола к полу ввода бренда: {str(e)}")

    # очистка поля бренда
    try:
        brands_field.clear()
        logger.debug("Поле ввода бренда очищено")
    except Exception as e:
        logger.error(f"Ошибка очистики поля ввода бренда: {str(e)}")
        return False

    # поиск кнопки "Импортировать" (для скрола)
    try:
        element = driver.find_element(
            "xpath", "//vaadin-button[text()='Импортировать']"
        )

        logger.debug('Кнопка "Импортировать" найдена')
    except Exception as e:
        logger.error(f"Ошибка скрола страницы вниз: {str(e)}")
        return False

    # скролл к кнопке "Импортировать"
    try:
        driver.execute_script(
            """
            const element = arguments[0];
            element.scrollIntoView({behavior: 'smooth', block: 'center'});
            window.scrollBy(0, -100);  // Подвинуть чуть выше, если что-то перекрывает
        """,
            element,
        )
        logger.debug('Скрол к кнопке "Импортировать" выполнен')
    except Exception as e:
        logger.error(f'Ошибка скрола к кнопке "Импортировать: {str(e)}"')
        return False

    sleep(micro_wait)

    # поиск кнопки "Импортировать" (для нажатия)
    try:
        import_product_button = search_element(
            driver, import_product_button_locator, wait
        )
        logger.debug("Кнопка импорта товара найдена")
    except Exception as e:
        logger.error(f"Ошибка поиска кнопки импорта товара: {str(e)}")
        return False

    try:
        import_product_button.click()
        logger.debug("Кнопка импорта товара нажата")
    except Exception as e:
        logger.error(f"Ошибка нажатия на кнопку импорта товара: {str(e)}")
        return False

    sleep(micro_wait)

    error_message = driver.find_elements(*error_message_locator)

    if (
            len(error_message) >= 1
    ):  # если найдено одно или более всплывающее окно с ошибкой
        logger.debug(f"Найден бракованный товар с артикулом {article}")

        try:
            help_button = search_element(driver, help_button_locator, wait)
            logger.debug('Кнопка "Поддержка" найдена')
        except Exception as e:
            logger.error(f'Ошибка поиска кнопки "Поддержка": {str(e)}')
            return False

        try:
            help_button.click()
            logger.debug('Кнопка "Поддержка" нажата')
        except Exception as e:
            logger.error(f'Ошибка нажатия на кнопку "Поддержка": {str(e)}')
            return False

        try:
            cross_button = search_element(driver, cross_button_locator, wait)
            logger.debug("Крестик найден")
        except Exception as e:
            logger.error(
                f"Ошибка поиска кнопки крестика, закрывающего окно поддержки: {str(e)}"
            )
            return False

        try:
            cross_button.click()
            logger.debug("Крестик нажат")
        except Exception as e:
            logger.error(
                f"Ошибка нажатия на кнопку крестика, закрывающего окно: {str(e)}"
            )
            return False

        try:
            with open(paths.data.broken_articles, "a") as f:
                f.write(f"\n{article}")
            logger.debug("Бракованный артикул сохранен в broken_articles.txt")
        except Exception as e:
            logger.error(
                "Ошибка сохранения бракованного артикула в broken_articles.txt"
            )
            return False

        return None

    return True
