import os
import subprocess as sp
from typing import Dict, Optional
from typing import List, TypeVar, Generic, Union

from utils._utilloader import JsonDict
from utils.config import ConfigName, ROOT_DIR
from utils.log import LOGGER


def run_os_cmd(cmd_list: list[str]) -> int:
    output = sp.run(cmd_list)
    return output.returncode


def kill_python() -> None:
    if os.name == "posix":
        run_os_cmd(["killall", "-9", "python"])
    else:
        run_os_cmd(["taskkill", "/F", "/IM", "python.exe"])


T = TypeVar('T')


class CollectionOwner(Generic[T]):
    """Class for list of items with one index.
    It is parent for SongPart, Filefinder"""

    def __init__(self, first: T):
        self.__items: List[T] = []
        self.__items.append(first)
        self.__undo: List[T] = []
        self.__id: int = 0
        self.__fixed: T = first
        self._collection_str: str = ""

    def get_fixed(self) -> T:
        if self.__fixed not in self.__items:
            self.__fixed = self.__items[0]
        return self.__fixed

    def set_fixed(self, fixed: T) -> None:
        if fixed not in self.__items:
            self.__items.append(fixed)
        self.__id = self.__items.index(fixed)
        self.__fixed = fixed

    def go_fixed(self) -> None:
        fixed = self.get_fixed()
        self.__id = self.__items.index(fixed)

    @property
    def fixed_id(self) -> int:
        fixed = self.get_fixed()
        return self.__items.index(fixed)

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

    def find_first_id(self, method) -> int:
        return next((x for x in range(self.item_count) if method(x)), -1)

    def find_first(self, method) -> Optional[T]:
        return next((x for x in self.__items if method(x)), None)

    def delete(self, k: int, save_undo: bool = False) -> T:
        if self.item_count <= 1 or k < 0 or k >= self.item_count:
            return None
        item = self.__items.pop(k)
        self._collection_str = ""
        if self.__id >= k:
            self.__id -= 1
            self.__id = max(0, self.__id)
        if save_undo:
            self.__undo.append(item)
        return item

    def undo(self) -> None:
        deleted = self.delete(self.item_count - 1)
        self.__undo.append(deleted)

    def redo(self) -> None:
        try:
            item = self.__undo.pop()
            self.__items.append(item)
            self._collection_str = ""
        except IndexError:
            pass

    def go_id(self, k: int) -> None:
        self.__id = k

    def get_id(self, k: int) -> T:
        return self.__items[k]

    def append(self, item: T) -> None:
        assert isinstance(item, type(self.__items[0]))
        self.__items.append(item)
        self.__undo.clear()
        self._collection_str = ""

    def get_item(self) -> T:
        return self.__items[self.__id]

    def set_item(self, item: T) -> None:
        self.__items[self.__id] = item

    def get_str(self) -> str:
        lst_size = min(7, len(self.__items))
        start_id = (self.__id // lst_size) * lst_size
        lst = self.__items[start_id:start_id + lst_size]
        roll_over_count = lst_size - len(lst)
        if roll_over_count > 0:
            lst = lst + self.__items[:roll_over_count]
        fixed = self.get_fixed()
        item = self.get_item()
        tmp: str = ""
        for elm in lst:
            elm_str = str(elm)
            if not elm_str:
                continue
            if elm is fixed:
                prefix = "*"
            elif elm is item:
                prefix = "~"
            else:
                prefix = " "
            tmp += prefix + elm_str + '\n'

        return tmp[:-1]

    def iterate(self, go_fwd: bool) -> None:
        self.__id += 1 if go_fwd else -1
        if self.__id >= self.item_count:
            self.__id = 0
        if self.__id < 0:
            self.__id = self.item_count - 1


class FileFinder(CollectionOwner[str]):

    def __init__(self, directory: str, is_file: bool, end_with: str):
        self.__end_with: str = end_with
        self.__dir: str = os.path.join(ROOT_DIR, directory)

        found_items: List[str] = [x for x in os.listdir(str(self.__dir))
                                  if self.__chk_match(self.__dir, x, is_file)]

        found_items.sort()
        if not found_items:
            found_items.append("")

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
        return os.path.join(self.__dir, self.get_item())

    def get_end_with(self) -> str:
        return self.__end_with

    def delete(self, k: int, save_undo: bool = False) -> None:
        self.go_id(k)
        path = self.get_full_name()
        deleted = CollectionOwner.delete(self, k)
        if deleted and os.path.isfile(path):
            os.remove(path)


class RedrawScreen:
    def __init__(self):
        self.header: str = ""
        self.description: str = ""
        self.content: str = ""
        self.update: str = ""
        self.loop_len: int = 0
        self.idx: int = 0
        self.is_stop: bool = True
        self.is_rec: bool = False

    def __str__(self):
        return f"{self.update}|{self.loop_len}|" \
               f"{self.idx}|{self.is_stop}|{self.is_rec}"


class MenuLoader:
    """ class loading mapping dict. from JSON files
    It parses directory for JSON files """

    def __init__(self, load_dir: str, map_name: str, map_id: str):
        ff = FileFinder(load_dir, True, ".json")
        self.__map_name: str = map_name
        self.__map_id: str = map_id
        self.__items: Dict[str, Dict[str, Dict]] = dict()

        for _ in range(ff.item_count):
            file: str = str(ff.get_full_name())
            item: str = ff.get_item()[:-len(ff.get_end_with())]
            ff.iterate(True)
            LOGGER.info(f"Loading control config from {file}")
            loader = JsonDict(file)
            default_dic = loader.get(ConfigName.default_config, dict())
            dic1 = dict()

            for key in [x for x in loader.dic() if x not in [ConfigName.default_config, ConfigName.comment]]:
                value = loader.get(key, None)
                assert type(value) == dict, f"Must be dictionary key={key} in file {item}"
                assert len(value) > 0, f"Dictionary must be non empty key={key} in file {item}"
                dic1[key] = dict(default_dic, **value)

            self.__items[item] = dic1

    def get(self, key: str) -> Union[List, str]:
        try:
            return self.__items[self.__map_name][self.__map_id][key]
        except KeyError:
            return ""

    def change_map(self, new_id: str, new_name: str) -> None:
        LOGGER.debug(f"{self.__class__.__name__} change_map: {new_name}, {new_id}")
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
            LOGGER.error(f"{self.__class__.__name__} change_map, incorrect name, id: {new_name}, {new_id}")

    def __str__(self):
        return self.__class__.__name__ + ": " + str(self.__items)


if __name__ == "__main__":
    def test1():
        lst = [chr(k) for k in range(65, 80)]
        co = CollectionOwner(lst[0])
        for k in lst[1:]:
            co.append(k)
        find1 = co.find_first_id(lambda x: co.get_id(x) == 'F')
        assert find1 == 5, f"found: {find1} expected: 5"
        co.go_id(8)  # letter I
        list_str = co.get_str()
        print(list_str)
        assert "H" == list_str[0]
        assert "~I" in list_str


    def test2():
        ff = FileFinder(".", True, "")
        for k in range(ff.item_count):
            print(ff.get_id(k))

        find1 = ff.find_first_id(lambda x: 'l' in ff.get_id(x))
        assert find1 >= 0


    def test3():
        ff = FileFinder(".", True, ".lkjlkjhkj")
        print(ff.get_item())
        print(ff.item_count)
        assert "" == ff.get_item()


    test1()
    test2()
    test3()
