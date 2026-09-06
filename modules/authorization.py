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


def autorization(driver, wait):
    # получение логина и пароля
    try:
        with open(paths.user_data.personal_data, "r", encoding="utf8") as f:
            data = json.load(f)
            login = data["login"]
            password = data["password"]
            logger.debug(
                f"Из personal_data.json получено: login={login}, password={password}"
            )
    except Exception as e:
        logger.error(
            f"Ошибка получения логина и пароля из personal_data.json: {str(e)}"
        )
        return False

    # получение локаторов
    try:
        with open(paths.data.locators, "r", encoding="utf8") as f:
            data = json.load(f)
            login_locator = tuple(data["login_locator"].split("&"))
            password_locator = tuple(data["password_locator"].split("&"))
            submit_button_locator = tuple(
                data["submit_button_locator"].split("&"))
            logger.debug(
                f"Из locator.json получено: login_locator={login_locator}, password_locator={password_locator}, submit_button_locator={submit_button_locator}"
            )
    except Exception as e:
        logger.error(f"Ошибка получения локаторов из locators.json: {str(e)}")
        return False

    # поиск поля логина
    try:
        login_field = search_element(driver, login_locator, wait)
        logger.debug("Поле ввода логина найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля ввода логина: {str(e)}")
        return False

    # поиск поля пароля
    try:
        password_field = search_element(driver, password_locator, wait)
        logger.debug("Поле ввода пароля найдено")
    except Exception as e:
        logger.error(f"Ошибка поиска поля ввода пароля: {str(e)}")
        return False

    # поиск кнопки "Войти"
    try:
        submit_button = search_element(driver, submit_button_locator, wait)
        logger.debug('Кнопка "Войти" найдена')
    except Exception as e:
        logger.error(f'Ошибка поиска кнопки "Войти": {str(e)}')
        return False

    # ввод логина
    try:
        login_field.send_keys(login)
        logger.debug("Логин  введен")
    except Exception as e:
        logger.error(f"Ошибка ввода логина: {str(e)}")
        return False

    # ввод пароля
    try:
        password_field.send_keys(password)
        logger.debug("Пароль введен")
    except Exception as e:
        logger.error(f"Ошибка ввода пароля: {str(e)}")
        return False

    # нажатие на кнопку "Войти"
    try:
        submit_button.click()
        logger.debug('Кнопка "Войти" нажата')
    except Exception as e:
        logger.error(f'Ошибка нажатия на кнопку "Войти": {str(e)}')
        return False

    # проверка на некорректность логина/пароля
    if "error" in driver.current_url:
        logger.error("В форму регистрации введены неверные данные")
        return False

    return True
