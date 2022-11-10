from json import dump, load
from pathlib import Path
from typing import Dict, Union

ROOT_DIR = Path(__file__).parent.parent


class JsonDictLoader:
    def __init__(self, filename: Union[str, Path]):
        self.data: Dict
        self.__filename = Path(ROOT_DIR, filename)
        self.__filename.parent.mkdir(parents=True, exist_ok=True)
        # noinspection PyBroadException
        try:
            with open(self.__filename) as f:
                self.data = load(f)

            if not isinstance(self.data, dict):
                raise RuntimeError("JSON file must have dictionary {self.__filename}")

        except Exception:
            self.data = dict()
            self.save()

    def save(self) -> None:
        with open(self.__filename, "w") as f:
            dump(self.data, f, indent=2)

    def get_filename(self):
        return self.__filename

    def set_defaults(self, default_dic: Dict) -> None:
        self.data = dict(default_dic, **self.data)


CONFLDR = JsonDictLoader("save_song/looper_defaults.json")

if __name__ == "__main__":
    def test():
        CONFLDR.set_defaults({1: 2, 30: 50})
        print(CONFLDR.data)

        CONFLDR.data = {"aa": "bb"}
        print(CONFLDR.data)


    test()
