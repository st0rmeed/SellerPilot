import logging.config
import json
import os
from datetime import datetime

with open("data/log.json", "r", encoding="utf8") as f:
    config = json.load(f)

# Генерация пути для логов
logs_base_dir = "logs"
current_date = datetime.now()
month_dir = current_date.strftime("%Y-%m")
log_filename = current_date.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
log_filepath = os.path.join(logs_base_dir, month_dir, log_filename)

# Создание директорий
os.makedirs(os.path.dirname(log_filepath), exist_ok=True)

# Важное изменение: закрываем предыдущие обработчики
if logging.getLogger("cl_utils_file").hasHandlers():
    for handler in logging.getLogger("cl_utils_file").handlers:
        handler.close()
        logging.getLogger("cl_utils_file").removeHandler(handler)

# Обновление конфигурации обработчика
config["handlers"]["cl_utils_file"]["filename"] = log_filepath

# Применение конфигурации
logging.config.dictConfig(config)

logger = logging.getLogger("cl_utils_file")
