import json
from pathlib import Path

class Config:
    _config_data = None

    @classmethod
    def load(cls, file_path: str = "config/config.json"):
        if cls._config_data is None:
            config_file = Path(file_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {file_path}")
            with open(config_file, "r", encoding="utf-8") as f:
                cls._config_data = json.load(f)

    @classmethod
    def get(cls, key: str, default=None):
        if cls._config_data is None:
            cls.load()
        return cls._config_data.get(key, default)

    @classmethod
    def all(cls):
        if cls._config_data is None:
            cls.load()
        return cls._config_data
