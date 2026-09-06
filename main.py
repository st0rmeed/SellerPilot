import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QLabel,
    QPushButton,
    QListView,
    QHBoxLayout,
    QMainWindow,
)
from PyQt6.QtCore import Qt, QStringListModel, QThread, pyqtSignal
from PyQt6.QtGui import QFont

import qdarkstyle

import json

from modules.script import main
from modules.log import logger
from config import load_paths

try:
    paths = load_paths('paths.json')
    logger.debug('Данные о путях из файла успешно получены')
except Exception as e:
    logger.critical(f'Ошибка вызова функции для получения путей: {e}')
    sys.exit()

# получeние данных из настроек
try:
    with open(paths.user_data.settings, "r", encoding="utf8") as f:
        json_data = json.load(f)
        # создание шрифтов
        font1 = QFont(
            json_data["font1"].split(";")[0], int(
                json_data["font1"].split(";")[1])
        )
        font2 = QFont(
            json_data["font2"].split(";")[0], int(
                json_data["font2"].split(";")[1])
        )
        checkbox_size = json_data["checkbox_size"]
        logger.debug(
            f"Из settings.json получено: font1={font1}, font2={font2}, checkbox_size={checkbox_size}"
        )
except Exception as e:
    logger.error(f"Ошибка получения данных из settings.json: {str(e)}")


# класс для многопоточной работы, чтобы pyqt6 и selenium не боролись за GUI
class WorkerThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

    def run(self):
        result = main(self.data)
        self.result_ready.emit(str(result))


# основное окно
class MainWindow(QMainWindow):
    def __init__(self, categories, font1, font2, cb_size):
        super().__init__()
        self.setWindowTitle("SellerPilot")
        self.setGeometry(0, 0, 1000, 600)

        # таблица категорий
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setParent(self)
        self.table.setHorizontalHeaderLabels(["Категория", "Выбрано"])
        self.table.horizontalHeader().setFont(font1)
        self.table.setRowCount(len(categories))
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(font1)
        self.table.setGeometry(20, 60, 850, 450)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(0, 700)

        # кнопка запуска
        self.run_button = QPushButton("Запустить", self)
        self.run_button.setFont(font2)
        self.run_button.setGeometry(150, 920, 150, 50)
        self.run_button.clicked.connect(self.run)

        # вывод выбранных значений
        self.selected_values_list_view = QListView(self)
        self.selected_values_list_view.setGeometry(890, 60, 1010, 450)
        self.selected_values_list_view.setFont(font1)

        # вывод бракованных артикулов
        self.defective_products_list_view = QListView(self)
        self.defective_products_list_view.setGeometry(890, 580, 1010, 300)
        self.defective_products_list_view.setFont(font1)

        # акутальные выбранные данные
        self.model = QStringListModel()
        self.selected_values_list_view.setModel(self.model)

        # бирки
        self.categories_label = QLabel("Доступные категории", self)
        self.selected_values_label = QLabel("Выбранные категории", self)
        self.defective_products_label = QLabel("Бракованные артикулы", self)
        self.warehouses_label = QLabel("Склады", self)
        self.defective_products_label.setFont(font2)
        self.categories_label.setFont(font2)
        self.selected_values_label.setFont(font2)
        self.warehouses_label.setFont(font2)
        self.categories_label.setGeometry(275, 10, 300, 50)
        self.selected_values_label.setGeometry(1300, 10, 300, 50)
        self.warehouses_label.setGeometry(400, 530, 100, 50)
        self.defective_products_label.setGeometry(1300, 530, 300, 50)

        self.result_label = QLabel("", self)
        self.result_label.setFont(font2)
        self.result_label.setGeometry(800, 920, 400, 50)

        # создание таблицы
        for row, category in enumerate(categories):
            # колонка 1: название категории
            item = QTableWidgetItem(category)
            item.setFlags(item.flags() and Qt.ItemFlag.ItemIsEditable)
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft and Qt.AlignmentFlag.AlignTop
            )
            self.table.setItem(row, 0, item)

            # колонка 2: чекбокс
            checkbox = QCheckBox()
            checkbox.setStyleSheet(
                f"QCheckBox::indicator {{ width: {cb_size}; height: {cb_size}; }}"
            )
            # подключение функции на выбор и снятие чекбокса
            checkbox.stateChanged.connect(
                lambda state, cat=category: self.choose_warehouse(state, cat)
            )
            # расположение по центру
            container = QWidget()
            grid = QHBoxLayout(container)
            grid.addWidget(checkbox, alignment=Qt.AlignmentFlag.AlignCenter)
            grid.setContentsMargins(0, 0, 0, 0)  # удаление отступов
            grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # расположение виджета в таблице
            self.table.setCellWidget(row, 1, container)

        # переменная, на основе которой строится модель QListView -> сам QListView
        self.selected_dict = {}

        # самый простой способ сделать декоративный прямоугольник :)
        self.design_list_view = QListView(self)
        self.design_list_view.setGeometry(20, 580, 850, 300)

        x, y = 10, 10
        # создание бирок отображения складов
        self.label1 = QLabel("Москва", self)
        self.label2 = QLabel("Санкт-Петербург", self)
        self.label3 = QLabel("Екатеринбург", self)
        self.label1.setGeometry(10, 10, 200, 50)
        self.label2.setGeometry(200, 10, 200, 50)
        self.label3.setGeometry(390, 10, 200, 50)
        self.label1.setFont(font1)
        self.label2.setFont(font1)
        self.label3.setFont(font1)

        # создание чекбоксов выбора склада
        self.checkbox1 = QCheckBox(self)
        self.checkbox2 = QCheckBox(self)
        self.checkbox3 = QCheckBox(self)
        # изменение размеров чекбоксов
        self.checkbox1.setStyleSheet(
            f"QCheckBox::indicator {{ width: {cb_size}; height: {cb_size}; }}"
        )
        self.checkbox2.setStyleSheet(
            f"QCheckBox::indicator {{ width: {cb_size}; height: {cb_size}; }}"
        )
        self.checkbox3.setStyleSheet(
            f"QCheckBox::indicator {{ width: {cb_size}; height: {cb_size}; }}"
        )

        # перемещений бирок
        x, y = 150, 650
        self.label1.move(x, y)
        self.label2.move(x + 190, y)
        self.label3.move(x + 440, y)

        # перемещение чекбоксов
        self.checkbox1.move(x + 30, y + 80)
        self.checkbox2.move(x + 270, y + 80)
        self.checkbox3.move(x + 500, y + 80)

        # заполнение виджета бракованных товаров
        with open(paths.data.broken_articles, "r") as f:
            data = [
                line.strip("\n") for line in f.readlines() if line.strip("\n") and line
            ]

        model2 = QStringListModel()
        model2.setStringList(data)
        self.defective_products_list_view.setModel(model2)

        # открытие в полноэкранном режиме
        self.showMaximized()

    # выбор склада
    def choose_warehouse(self, state, category):
        # если галочка поставлена
        if state == Qt.CheckState.Checked.value:
            selected_warehouses = []
            if self.checkbox1.isChecked():
                selected_warehouses.append("Москва")
            if self.checkbox2.isChecked():
                selected_warehouses.append("Санкт-Петербург")
            if self.checkbox3.isChecked():
                selected_warehouses.append("Екатеринбург")
            self.selected_dict[category] = sorted(selected_warehouses)
            self.update_list_view()

        else:  # если галочка снята
            if category in self.selected_dict:
                del self.selected_dict[category]
                self.update_list_view()

    # запуск скрипта
    def run(self):
        if not self.selected_dict:
            self.show_result("Нет выбранных категорий")
            return
        else:
            for key, value in self.selected_dict.items():
                if not value:
                    self.show_result(f'Не выбран склад категории "{key}"')
                    return
            self.show_result("")
            self.worker = WorkerThread(self.selected_dict)
            self.worker.result_ready.connect(self.show_result)
            self.worker.start()

    # отображение результата
    def show_result(self, result):
        self.result_label.setText(result)
        self.result_label.adjustSize()

        with open(paths.data.broken_articles, "r", encoding="utf8") as f:
            data = [
                line.strip("\n") for line in f.readlines() if line.strip("\n") and line
            ]

        model2 = QStringListModel()
        model2.setStringList(data)
        self.defective_products_list_view.setModel(model2)

    # отображение актуального списка выбранных элементов
    def update_list_view(self):
        current_list = [
            f"{key}: {', '.join(list(sorted(value)))}"
            for key, value in self.selected_dict.items()
        ]
        self.model.setStringList(current_list)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        with open(paths.user_data.categories, "r", encoding="utf8") as f:
            categories = [
                category.strip("\n")
                for category in f.readlines()
                if category.strip("\n") and category
            ]
        logger.debug("Из categories.txt получены категории товаров")
    except Exception as e:
        logger.error(
            f"Ошибка считывания категорий из categories.txt: {str(e)}")

    window = MainWindow(categories, font1, font2, checkbox_size)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    window.show()
    sys.exit(app.exec())
