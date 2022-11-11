from json import dump, load
from pathlib import Path
from typing import Dict, Union, Any

ROOT_DIR = Path(__file__).parent.parent


class JsonDict:
    def __init__(self, filename: Union[str, Path]):
        self.__dic: Dict[str, Any] = dict()
        self.__filename = Path(ROOT_DIR, filename)
        self.__filename.parent.mkdir(parents=True, exist_ok=True)
        # noinspection PyBroadException
        try:
            with open(self.__filename) as f:
                self.__dic = load(f)

            if not isinstance(self.dic, dict):
                raise RuntimeError("JSON file must have dictionary {self.__filename}")

        except Exception:
            self.__dic = dict()
            self.save()

    @property
    def dic(self) -> Dict:
        return self.__dic

    def save(self) -> None:
        with open(self.__filename, "w") as f:
            dump(self.__dic, f, indent=2)

    def get_filename(self) -> Path:
        return self.__filename

    def set(self, k, v) -> None:
        self.__dic[k] = v

    def set_defaults(self, default_dic: Dict) -> None:
        self.__dic = dict(default_dic, **self.__dic)


CONFLDR = JsonDict("config/looper_defaults.json")

if __name__ == "__main__":
    def test():
        CONFLDR.set_defaults({"1": 2, "30": 50})
        print(CONFLDR.dic)

        CONFLDR.set_defaults({"aa": "bb"})
        print(CONFLDR.dic)


    test()
