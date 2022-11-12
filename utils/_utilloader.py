from json import dump, load
from pathlib import Path
from typing import Dict, Any

ROOT_DIR = Path(__file__).parent.parent


class JsonDict:
    def __init__(self, filename: str):
        self.__dic: Dict[str, Any] = dict()
        self.__filename: str = str(Path(ROOT_DIR, filename))
        # noinspection PyBroadException
        try:
            with open(self.__filename) as f:
                self.__dic = load(f)

            if not isinstance(self.__dic, dict):
                raise RuntimeError("JSON file must have dictionary {self.__filename}")

        except Exception:
            self.save()

    def dic(self) -> Dict:
        return self.__dic

    def save(self) -> None:
        if self.__filename:
            with open(self.__filename, "w") as f:
                dump(self.__dic, f, indent=2)

    def get_filename(self) -> str:
        return self.__filename

    def get_dir(self) -> str:
        return str(Path(self.__filename).parent)

    def get(self, k, default) -> Any:
        return self.__dic.get(k, default)

    def set(self, k, v) -> None:
        self.__dic[k] = v

    def set_defaults(self, default_dic: Dict) -> None:
        self.__dic = dict(default_dic, **self.__dic)


if __name__ == "__main__":
    pass
