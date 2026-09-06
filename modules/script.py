try:
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    import json
    from time import sleep
    from datetime import datetime
    import sys

    # в комменты для удобства вынесено то, что нужно для запуска ф-и
    from modules.log import logger
    from modules.authorization import autorization  # driver, wait
    from modules.set_prices import set_prices  # driver
    from modules.check_chekboxes import check_checkboxes  # driver, wait
    from modules.import_product import import_product  # driver, wait, micro_wait
    from modules.select_combo_value import select_combo_value  # driver, xpath, desired_value
    from modules.install_remove_checkbox import install_remove_checkbox  # driver, wait
    from config import load_paths

    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    from config import load_paths

    try:
        paths = load_paths('paths.json')
        logger.debug('Данные о путях из файла успешно получены')
    except Exception as e:
        logger.critical(f'Ошибка вызова функции для получения путей: {e}')
        sys.exit()


    def main(selected_dict):
        try:
            with open(paths.user_data.settings, "r", encoding="utf8") as f:
                data = json.load(f)
                wait = float(data["wait"])
                screen_size = list(
                    map(lambda x: int(x), data["screen_size"].split(";"))
                )
                warehouses_xpath = data["warehouses_xpath"]
                categories_xpath = data["categories_xpath"]
                micro_wait = float(data["micro_wait"])
                brands = data["brands"].split(";")
                start_index = int(data["start_index"])
                end_index = int(data["end_index"])
                sleep_time = float(data["sleep_time"])
                count_clicks_on_import_button = int(
                    data["count_clicks_on_import_button"]
                )

                logger.debug(
                    f"Из settings.json получено: wait={wait}, screen_size={screen_size}, warehouses_xpath={warehouses_xpath}, categories_xpath={categories_xpath}, micro_wait={micro_wait}, brands={brands}, start_index={start_index}, end_index={end_index}, sleep_time={sleep_time}, count_clicks_on_import_button={count_clicks_on_import_button}"
                )
        except Exception as e:
            logger.error(f"Ошибка получения данных из settings.json: {str(e)}")
            driver.quit()
            return "Ошибка получения данных из settings.json"

        try:
            service = Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            logger.debug("Сервис и драйвер созданы")
        except Exception as e:
            logger.error(f"Ошибка создания сервиса или драйвера: {str(e)}")
            driver.quit()
            return "Ошибка создания сервиса или драйвера"

        try:
            driver.get("https://sellerpilot.ru/catalog-v2")
            driver.set_window_size(*screen_size)
            logger.debug("Сайт открыт, размер окна изменен")
        except Exception as e:
            logger.error(
                f"Ошибка открытия сайта или изменения размера окна: {str(e)}")
            driver.quit()
            return "Ошибка открытия страницы или изменения размеров экрана"

        logger.debug("Начата авторизация на сайте")
        if not autorization(driver, wait):
            driver.quit()
            return "Ошибка авторизации на сайте"

        # очистка файла перед запуском с помощью открытия в формате W
        try:
            open("data/progress.txt", "w").close()
            logger.debug("Файл progress.txt очищен")
        except Exception as e:
            logger.error(
                f"Ошибка очистки файла progress.txt перед запуском: {str(e)}")
            driver.quit()
            return "Ошибка очистки файла progress.txt перед запуском"

        articles = []
        count_imports = 0
        progress_categories, progress_warehouses = -1, 0
        total_categories = len(selected_dict.keys())

        for category, warehouses in selected_dict.items():
            progress_categories += 1
            logger.debug('Начат процесс изменения полей "Цена от" и "Цена до"')
            if not set_prices(driver):
                driver.quit()
                return "Ошибка установления цен"

            logger.debug("Начата проверка чекбоксов")
            if not check_checkboxes(driver, wait):
                driver.quit()
                return "Ошибка проверки чекбоксов"

            logger.debug(f"Начат выбор категории {category}")
            if not select_combo_value(driver, categories_xpath, category):
                driver.quit()
                return "Ошибка выбора категории"

            try:
                with open(paths.data.progress, "a", encoding="utf8") as f:
                    f.write(
                        f"\n{datetime.now()} - начата работа над категорией {category} (завершено {progress_categories}/{total_categories} категорий)\n"
                    )
                logger.debug("В progress.txt записана текущая категория")
            except Exception as e:
                logger.error(
                    f"Ошибка записи текущей категории в progress.txt: {str(e)}"
                )

            logger.debug(f"Начата работа над категорией {category}")

            progress_warehouses = 0
            total_warehouses = len(selected_dict[category])
            for warehouse in warehouses:
                sleep(micro_wait)
                logger.debug(
                    f"Начат процесс выбора значения склада {warehouse}")
                if not select_combo_value(driver, warehouses_xpath, warehouse):
                    driver.quit()
                    return "Ошибка выбора склада"

                flag = True
                while flag:
                    line_index = start_index
                    while line_index < end_index:
                        if count_imports >= count_clicks_on_import_button:

                            logger.debug("Программа уходит в сон")
                            sleep(sleep_time)
                            logger.debug("Программа вышла из сна")

                            logger.debug(
                                "Начат процесс обновления страницы при помощи чекбокса"
                            )
                            if not install_remove_checkbox(driver, wait):
                                driver.quit()
                                return "Ошибка обновления страницы чекбоксом"
                            sleep(5 * micro_wait)

                            line_index = start_index
                            count_imports = 0

                        sleep(2 * micro_wait)

                        # поиск следующего бренда, try-except для проверки конца списка товаров
                        try:
                            brand_field = WebDriverWait(driver, wait).until(
                                EC.visibility_of_element_located(
                                    (
                                        "xpath",
                                        f"//vaadin-grid-cell-content[@slot='vaadin-grid-cell-content-{line_index}2']",
                                    )
                                )
                            )
                        except Exception as e:
                            progress_warehouses += 1

                            try:
                                with open(
                                        paths.data.progress, "a", encoding="utf8"
                                ) as f:
                                    f.write(
                                        f"{datetime.now()} - склад {warehouse} импортирован (завершено {progress_warehouses}/{total_warehouses} складов)\n"
                                    )
                                logger.debug(
                                    f"Склад {warehouse} импортирован и записан в progress.txt ({progress_warehouses}/{total_warehouses})"
                                )

                            except Exception as e:
                                logger.error(
                                    f"Ошибка записи текущего склада в progress.txt: {str(e)}"
                                )
                                driver.quit()
                                return "Ошибка записи прогресса в progress.txt"

                            flag = False  # выход из "while flag", переход к следующему складу
                            break

                        try:
                            article_field = WebDriverWait(driver, wait).until(
                                EC.visibility_of_element_located(
                                    (
                                        "xpath",
                                        f"//vaadin-grid-cell-content[starts-with(@slot, 'vaadin-grid-cell-content-{line_index}4')]",
                                    )
                                )
                            )
                            logger.debug(
                                f"Следующий артикул {article_field.text} найден"
                            )
                        except Exception as e:
                            logger.error(
                                f"Ошибка поиска следующего артикула: {str(e)}")
                            driver.quit()
                            return "Ошибка поиска следующего артикула"

                        # скрол к артикулу
                        try:
                            driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});",
                                article_field,
                            )
                            logger.debug(
                                "Скрол к следующему артикулу выполнен")
                        except Exception as e:
                            logger.error(
                                f"Ошибка скрола к следующему артикулу: {str(e)}"
                            )
                            driver.quit()
                            return "Ошибка скрола к следующему артикулу"

                        try:
                            with open(
                                    "data/broken_articles.txt", "r", encoding="utf8"
                            ) as f:
                                lines = [item.strip("\n")
                                         for item in f.readlines()]
                                articles.extend(lines)
                            logger.debug(
                                "Список бракованных артикулов получен")
                        except Exception as e:
                            logger.error(
                                f"Ошибка получения бракованных артикулов: {str(e)}"
                            )
                            driver.quit()
                            return "Ошибка получения списка бракованных артикулов"

                        if (
                                brand_field.text in brands
                                and article_field.text not in articles
                        ):
                            try:
                                button = WebDriverWait(driver, wait).until(
                                    EC.visibility_of_element_located(
                                        (
                                            "xpath",
                                            f"//vaadin-grid-cell-content[starts-with(@slot, 'vaadin-grid-cell-content-{line_index}0')]//vaadin-button",
                                        )
                                    )
                                )
                                logger.debug("Кнопка импорта товара найдена")
                            except Exception as e:
                                logger.error(
                                    f"Ошибка поиска кнопки импорта товара: {str(e)}"
                                )
                                driver.quit()
                                return "Ошибка поиска кнопки импорта товара"

                            try:
                                button.click()
                                logger.debug("Кнопка импорта товара нажата")
                            except Exception as e:
                                logger.error(
                                    f"Ошибка нажатия на кнопку импорта товара: {str(e)}"
                                )
                                driver.quit()
                                return "Ошибка нажатия на кнопку импорта товара"

                            logger.debug(
                                f"Начат импорт товара с brand={brand_field.text} и article={article_field.text}"
                            )
                            result = import_product(
                                driver, wait, micro_wait, article_field.text
                            )
                            if result:  # если успех
                                logger.debug("Товар импортирован")
                                count_imports += 1
                            elif (
                                    result == False
                            ):  # возникла ошибка в результате работы модуля
                                driver.quit()
                                return "Ошибка импорта товара"
                            elif result == None:  # категория в списке бракованных
                                logger.debug(
                                    "Данный товар является бракованным")

                        line_index += 1

            driver.refresh()

        driver.quit()
        return "Все товары импортированы"


    if __name__ == "__main__":
        print(main({"Освещение": ["Санкт-Петербург"]}))
except Exception as e:
    logger.critical(f"Непредвиденная ошибка: {str(e)}")
