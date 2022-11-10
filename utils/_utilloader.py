from json import dump, load
from pathlib import Path
from typing import Any, Dict, Union
from typing import List

ROOT_DIR = Path(__file__).parent.parent


class JsonDictLoader:
    def __init__(self, filename: Union[str, Path]):
        self.__filename = Path(ROOT_DIR, filename)
        self.__filename.parent.mkdir(parents=True, exist_ok=True)
        self.__app_dict: Dict[str, Any] = dict()

        with open(self.__filename) as f:
            self.__app_dict = load(f)

        if not isinstance(self.__app_dict, dict):
            raise RuntimeError("JSON file must have dictionary {self.__filename}")
        if len(self.__app_dict) == 0:
            raise RuntimeError("JSON file must have non empty dictionary {self.__filename}")

    def save(self) -> None:
        with open(self.__filename, "w") as f:
            dump(self.__app_dict, f, indent=2)

    def set(self, key: str, value: Any) -> None:
        self.__app_dict[key] = value

    def get(self, key: str, default) -> Any:
        return self.__app_dict.get(key, default)

    def add_if_missing(self, key: str, default) -> None:
        if key not in self.__app_dict:
            self.__app_dict[key] = default

    def get_keys(self) -> List[str]:
        return [*self.__app_dict]

    def get_filename(self):
        return self.__filename


class ConfigLoader:
    """class will only static methods to keep app's main configs"""
    __jdl: JsonDictLoader = JsonDictLoader("save_song/looper_defaults.json")

    @staticmethod
    def get_dict() -> JsonDictLoader:
        return ConfigLoader.__jdl

    @staticmethod
    def set_dict(dl: JsonDictLoader) -> None:
        ConfigLoader.__jdl = dl

    @staticmethod
    def get(key: str, default) -> Any:
        return ConfigLoader.__jdl.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        return ConfigLoader.__jdl.set(key, value)

    @staticmethod
    def save() -> None:
        return ConfigLoader.__jdl.save()


if __name__ == "__main__":
    pass
