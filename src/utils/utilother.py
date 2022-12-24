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

    def item_count(self) -> int:
        return len(self.__items)

    def get_id(self) -> int:
        return self.__id

    def set_id(self, k: int) -> None:
        self.__id = k

    def apply_to_each(self, method, use_undo: bool = False) -> None:
        lst = self.__items + (self.__undo if use_undo else [])
        for x in lst:
            method(x)

    def find_first(self, method) -> Optional[T]:
        return next((x for x in self.__items if method(x)), None)

    def delete(self) -> T:
        if self.item_count() <= 1:
            return None
        item = self.__items.pop(self.__id)
        self._collection_str = ""
        self.__id = 0
        return item

    def undo(self) -> bool:
        if self.item_count() <= 1:
            return False
        item = self.__items.pop()
        self.__id = 0
        self.__undo.append(item)
        self._collection_str = ""
        return True

    def redo(self) -> bool:
        if not self.__undo:
            return False
        item = self.__undo.pop()
        self.__items.append(item)
        self._collection_str = ""
        return True

    def get_first(self) -> T:
        return self.__items[0]

    def find_item(self, item: T) -> int:
        return self.__items.index(item)

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
        if self.__id >= self.item_count():
            self.__id = 0
        if self.__id < 0:
            self.__id = self.item_count() - 1

    def __str__(self):
        return f"{len(self.__items):02}/{len(self.__undo):02}"


# noinspection PyUnreachableCode
class CollectionOwnerExt(CollectionOwner[T]):

    def __init__(self, first: T):
        CollectionOwner.__init__(self, first)
        self.__fixed: T = first

    def get_fixed(self) -> T:
        return self.__fixed

    def set_fixed(self, item: T) -> None:
        self.attach(item)
        self.__fixed = item

    def fixed_id(self) -> int:
        return self.find_item(self.__fixed)

    def get_str(self, fixed: T = None) -> str:
        return super().get_str(self.__fixed)


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

    def delete(self, save_undo: bool = False) -> None:
        path = self.get_full_name()
        deleted = CollectionOwner.delete(self)
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
        found_list = list()
        co.apply_to_each(lambda x: found_list.append(x if x == 'F' else None))
        assert 'F' in found_list
        find1 = found_list.index('F')
        assert find1 == 5
        co.set_id(8)  # letter I
        assert "I" == co.get_item()
        list_str = co.get_str()
        print(list_str)
        assert ".7) H" in list_str
        assert "~8) I" in list_str


    def test2():
        ff = FileFinder(".", True, "")
        for k in range(ff.item_count()):
            print(ff.get_item())
            ff.iterate(True)
        print("================")
        found_list = list()
        ff.apply_to_each(lambda x: found_list.append(x if 'lo' in x else None))
        for item in [x for x in found_list if x]:
            print(item)


    def test3():
        ff = FileFinder(".", True, ".lkjlkjhkj")
        assert "" == ff.get_item()
        assert 1 == ff.item_count()


    test1()
    test2()
    test3()
