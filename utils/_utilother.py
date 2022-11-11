import logging
import os
import subprocess as sp
import sys
from pathlib import Path
from typing import Dict, Any
from typing import List, TypeVar, Generic, Union

from utils._utilconfig import ConfigName
from utils._utilloader import JsonDict

ROOT_DIR = Path(__file__).parent.parent

level = "WARN"
if "--debug" in sys.argv:
    level = "DEBUG"
if "--info" in sys.argv:
    level = "INFO"

logging.basicConfig(level=os.getenv("DEBUG_LEVEL", level), filename=Path(ROOT_DIR, 'log.log'), filemode='w')
LOGR = logging.getLogger()
fm = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
LOGR.handlers[0].setFormatter(fm)
LOGR.propagate = False

LOGR.info(f"=======>Starting looper's log {LOGR.handlers}")


def run_os_cmd(cmd_list: list[str]) -> int:
    output = sp.run(cmd_list)
    return output.returncode


T = TypeVar('T')


class CollectionOwner(Generic[T]):
    """Class for list of items with one index.
    It is parent for SongPart, Filefinder"""

    def __init__(self, first: T):
        self.__items: List[T] = []
        self.__items.append(first)
        self.__undo: List[T] = []
        self.__id: int = 0
        self._str = None

    @property
    def item_count(self) -> int:
        return len(self.__items)

    @property
    def undo_count(self) -> int:
        return len(self.__undo)

    @property
    def id(self) -> int:
        return self.__id

    def apply_to_each(self, method, use_undo: bool = False) -> None:
        lst = self.__items + (self.__undo if use_undo else [])
        for x in lst:
            method(x)

    def first_id(self, method, default: Any):
        return next((x for x in range(self.item_count) if method(x)), default)

    def delete(self, k: int, save_backup: bool) -> None:
        if self.item_count <= 1 or k < 0 or k >= self.item_count:
            return
        item = self.__items.pop(k)
        if save_backup:
            self.__undo.append(item)
        self._str = None
        if self.__id >= k:
            self.__id -= 1

    def undo(self) -> None:
        self.delete(self.item_count - 1, save_backup=True)

    def redo(self) -> None:
        try:
            item = self.__undo.pop()
            self.__items.append(item)
            self._str = None
        except IndexError:
            pass

    def go_id(self, k: int) -> None:
        self.__id = k

    def get_id(self, k: int) -> T:
        return self.__items[k]

    def go_last(self) -> None:
        self.__id = self.item_count - 1

    def append(self, item: T) -> None:
        self.__items.append(item)
        self.__undo.clear()
        self._str = None

    def get_item(self) -> T:
        return self.__items[self.__id]

    def get_first(self) -> T:
        return self.__items[0]

    def go_first(self) -> None:
        self.__id = 0

    def find_item_id(self, item: T) -> int:
        if item in self.__items:
            return self.__items.index(item)
        else:
            return -1

    def get_list(self, now_id: int = -1) -> str:
        tmp = ""
        lst_size = min(7, self.item_count)
        start_id = (self.__id // lst_size) * lst_size
        save_id = self.__id
        self.__id = start_id
        for _ in range(lst_size):
            prefix: str = ""
            if self.__id == now_id:
                prefix = "*"
            elif self.__id == save_id:
                prefix = "~"
            tmp += prefix + str(self.get_item()) + '\n'
            self.iterate(True)
        self.__id = save_id
        return tmp[:-1]

    def iterate(self, go_fwd: bool) -> None:
        self.__id += 1 if go_fwd else -1
        if self.__id >= self.item_count:
            self.__id = 0
        if self.__id < 0:
            self.__id = self.item_count - 1


class FileFinder(CollectionOwner[str]):
    def __init__(self, dir_name: str, is_file: bool, end_with: str):
        self.__end_with: str = end_with
        self.__dir: str = str(Path(ROOT_DIR, dir_name))

        found_items: List[str] = [x for x in os.listdir(str(self.__dir))
                                  if self.__chk_match(self.__dir, x, is_file)]

        found_items.sort(key=lambda x: os.path.getmtime(Path(self.__dir, x)), reverse=True)

        if not found_items:
            found_items.append("first" + self.__end_with)

        CollectionOwner.__init__(self, found_items[0])
        for item in found_items[1:]:
            self.append(item)

    def __chk_match(self, d: str, f: str, is_file: bool) -> bool:
        match1 = is_file == os.path.isfile(os.path.join(d, f))
        match2 = f.endswith(self.__end_with)
        return match1 and match2

    def get_dir_name(self) -> str:
        return self.__dir

    def get_full_name(self) -> str:
        return str(Path(self.__dir, self.get_item()))

    def get_end_with(self) -> str:
        return self.__end_with


class RedrawScreen:
    def __init__(self, content: str, update_method: str, loop_len: int, idx: int, is_stop: bool,
                 is_rec: bool):
        self.content: str = content
        self.update_method: str = update_method
        self.loop_len: int = loop_len
        self.idx: int = idx
        self.is_stop: bool = is_stop
        self.is_rec: bool = is_rec

    def __str__(self):
        return f"{self.update_method}|{self.loop_len}|" \
               f"{self.idx}|{self.is_stop}|{self.is_rec}"


class MenuLoader(FileFinder):
    """ class loading mapping dict. from JSON files
    It parses directory for JSON files """

    def __init__(self, load_dir: str, map_name: str, map_id: str):
        FileFinder.__init__(self, load_dir, True, ".json")
        self.__items: Dict[str, Dict] = self.__load_all()
        self.__map_name: str = map_name
        self.__map_id: str = map_id

    def __load_all(self) -> Dict[str, Dict[str, Dict]]:
        dic = dict()
        for _ in range(self.item_count):
            file: str = str(self.get_full_name())
            item: str = self.get_item()[:-len(self.get_end_with())]
            self.iterate(True)
            LOGR.info(f"Loading control config from {file}")
            loader = JsonDict(file)
            default_dic = loader.get(ConfigName.default_config, dict())
            dic1 = dict()

            for key in [x for x in loader.dic() if x not in [ConfigName.default_config, ConfigName.comment]]:
                value = loader.get(key, None)
                assert type(value) == dict, f"Must be dictionary key={key} in file {item}"
                assert len(value) > 0, f"Dictionary must be non empty key={key} in file {item}"
                dic1[key] = dict(default_dic, **value)

            dic[item] = dic1

        return dic

    def get(self, key: str) -> Union[List, str]:
        try:
            return self.__items[self.__map_name][self.__map_id][key]
        except KeyError:
            return ""

    def change_map(self, new_id: str, new_name: str) -> None:
        LOGR.debug(f"{self.__class__.__name__} change_map: {new_name}, {new_id}")
        # noinspection PyBroadException
        try:
            self.__map_name = new_name
            if new_id in ["prev", "next"]:
                lst = list(self.__items[self.__map_name])
                k = lst.index(self.__map_id)
                if new_id == "next":
                    k += 1
                    k = 0 if k >= len(lst) else k
                elif new_id == "prev":
                    k -= 1
                    k = len(lst) - 1 if k < 0 else k
                self.__map_id = lst[k]
            else:
                self.__map_id = new_id
            _ = self.__items[self.__map_name][self.__map_id]
        except Exception:
            LOGR.error(f"{self.__class__.__name__} change_map, incorrect name, id: {new_name}, {new_id}")

    def __str__(self):
        return self.__class__.__name__ + ": " + str(self.__items)


if __name__ == "__main__":
    pass
