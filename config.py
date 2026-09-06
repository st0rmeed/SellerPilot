import json
from dataclasses import dataclass
from pathlib import Path

from modules.log import logger


@dataclass
class UserData:
    categories: Path
    personal_data: Path
    settings: Path


@dataclass
class Data:
    broken_articles: Path
    locators: Path
    log: Path
    progress: Path


@dataclass
class FilePaths:
    user_data: UserData
    data: Data


def load_paths(file_path: str | Path) -> FilePaths:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            logger.debug(f'Данные из paths.json успешно прочитаны: {cfg}')
    except Exception as e:
        logger.critical(f'Ошибка чтения путей: {e}')

    # конвертируем строки из json в объекты Path
    return FilePaths(
        user_data=UserData(**{k: Path(v) for k, v in cfg["user_data"].items()}),
        data=Data(**{k: Path(v) for k, v in cfg["data"].items()})
    )
