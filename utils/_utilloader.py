from json import dump, load
from pathlib import Path
from typing import Dict, Union, Any

ROOT_DIR = Path(__file__).parent.parent


class JsonDict:
    def __init__(self, filename: Union[str, Path]):
        self.dic: Dict[str, Any] = dict()
        self.__filename = Path(ROOT_DIR, filename)
        self.__filename.parent.mkdir(parents=True, exist_ok=True)
        # noinspection PyBroadException
        try:
            with open(self.__filename) as f:
                self.dic = load(f)

            if not isinstance(self.dic, dict):
                raise RuntimeError("JSON file must have dictionary {self.__filename}")

        except Exception:
            self.dic = dict()
            self.save()

    def save(self) -> None:
        with open(self.__filename, "w") as f:
            dump(self.dic, f, indent=2)

    def get_filename(self) -> Path:
        return self.__filename

    def get(self, k, default) -> Any:
        return self.dic[k] if k in self.dic else default

    def set(self, k, v) -> None:
        self.dic[k] = v

    def set_defaults(self, default_dic: Dict) -> None:
        self.dic = dict(default_dic, **self.dic)


CONFLDR = JsonDict("save_song/looper_defaults.json")

if __name__ == "__main__":
    def test():
        CONFLDR.set_defaults({1: 2, 30: 50})
        print(CONFLDR.dic)

        CONFLDR.dic = {"aa": "bb"}
        print(CONFLDR.dic)


    test()
