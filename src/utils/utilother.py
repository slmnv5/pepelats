import os
from json import dump, load
# noinspection PyProtectedMember
from typing import Dict, Any
from typing import List, Optional
from typing import TypeVar, Generic

from utils._utilnumpy import get_stable_list
from utils.config import ROOT_DIR

T = TypeVar('T')


class DrawInfo:
    def __init__(self):
        self.update_method: str = ""
        self.header: str = ""
        self.text: str = ""
        self.content: str = ""
        self.loop_seconds: float = 0
        self.loop_position: float = 0
        self.is_stop: bool = True
        self.is_rec: bool = False

    def __str__(self):
        return f"{self.update_method}|{self.loop_seconds:2F}|" \
               f"{self.loop_position:2F}|{self.is_stop}|{self.is_rec}"


class CollectionOwner(Generic[T]):
    """Class for list of items with one index.
    It is parent for SongPart, Filefinder"""

    def __init__(self, first: T):
        self.__items: List[T] = []
        self.__items.append(first)
        self.__undo: List[T] = []
        self.__id: int = 0
        self._collection_str: str = ""

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

    def attach(self, item: T) -> None:
        """ add item only if not there, set id to added item"""
        assert isinstance(item, type(self.__items[0]))
        if item not in self.__items:
            self.__items.append(item)
        self.__undo.clear()
        self._collection_str = ""
        self.__id = self.__items.index(item)

    def get_item(self) -> T:
        return self.__items[self.__id]

    def set_item(self, item: T) -> None:
        self.__items[self.__id] = item

    def get_str(self, fixed: T = None) -> str:
        item_sub_list, id_sub_list = get_stable_list(self.__id, self.__items, 5)
        fixed_id = -1
        if fixed and fixed in self.__items:
            fixed_id = self.__items.index(fixed)

        result: str = ""
        for k in range(len(item_sub_list)):
            item: Any = item_sub_list[k]
            index: int = id_sub_list[k]
            item_str = str(index) + ") " + str(item)
            if index == fixed_id:
                prefix = "*"
            elif index == self.__id:
                prefix = "~"
            else:
                prefix = "."
            result += prefix + item_str + '\n'

        return result[:-1]

    def iterate(self, go_fwd: bool) -> None:
        self.__id += 1 if go_fwd else -1
        if self.__id >= self.item_count:
            self.__id = 0
        if self.__id < 0:
            self.__id = self.item_count - 1


class CollectionOwnerExt(CollectionOwner[T]):

    def __init__(self, first: T):
        CollectionOwner.__init__(self, first)
        self.__fixed: T = first

    def get_fixed(self) -> T:
        return self.__fixed

    def set_fixed(self, item: T) -> None:
        self.attach(item)
        self.__fixed = item

    def go_fixed(self) -> None:
        fixed = self.get_fixed()
        self.__id = self.__items.index(fixed)

    @property
    def fixed_id(self) -> int:
        fixed = self.get_fixed()
        return self.__items.index(fixed)


class FileFinder(CollectionOwner[str]):

    def __init__(self, directory: str, is_file: bool, end_with: str):
        self.__end_with: str = end_with
        self.__dir: str = ROOT_DIR + "/" + directory

        found_items: List[str] = [x for x in os.listdir(str(self.__dir))
                                  if self.__chk_match(self.__dir, x, is_file)]

        found_items.sort()
        if not found_items:
            found_items.append("")

        CollectionOwner.__init__(self, found_items[0])
        for item in found_items[1:]:
            self.attach(item)

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


class JsonDict:
    def __init__(self, filename: str):
        self.__dic: Dict[str, Any] = dict()
        self.__filename: str = filename
        with open(self.__filename) as f:
            self.__dic = load(f)
        if not isinstance(self.__dic, dict):
            raise RuntimeError("JSON file must have dictionary {self.__filename}")

    def dic(self) -> Dict:
        return self.__dic

    def save(self) -> None:
        if self.__filename:
            with open(self.__filename, "w") as f:
                dump(self.__dic, f, indent=2)

    def get_filename(self) -> str:
        return self.__filename

    def get_dir(self) -> str:
        return os.path.dirname(self.__filename)

    def get(self, k, default) -> Any:
        return self.__dic.get(k, default)

    def set(self, k, v) -> None:
        self.__dic[k] = v

    def set_defaults(self, default_dic: Dict) -> None:
        self.__dic = dict(default_dic, **self.__dic)


if __name__ == "__main__":
    def test1():
        lst = [chr(k) for k in range(65, 80)]
        co = CollectionOwner(lst[0])
        for k in lst[1:]:
            co.attach(k)
        find1 = co.find_first_id(lambda x: co.get_id(x) == 'F')
        assert find1 == 5, f"found: {find1} expected: 5"
        co.go_id(8)  # letter I
        assert "I" == co.get_item()
        list_str = co.get_str()
        assert " H" == list_str[0:2]
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
