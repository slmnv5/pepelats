from __future__ import annotations

import os
from typing import TypeVar, Generic

T = TypeVar('T')


def _stable_sub_list(idx: int, items: list[any], sub_list_size: int) -> list[any]:
    """ Sub list of elements surrounding item. If item changes sub list stays the same if
     item is still included in the sub list. Otherwise, all is recalculated."""
    lst_size: int = min(sub_list_size, len(items))
    start_idx: int = (idx // lst_size) * lst_size
    stop_idx: int = start_idx + lst_size
    if stop_idx < len(items):
        return items[start_idx:stop_idx]
    else:
        return items[start_idx:] + items[:stop_idx % len(items)]


class DrawInfo:
    def __init__(self):
        self.update_method: str = ""
        self.header: str = ""
        self.description: str = ""
        self.content: str = ""
        self.loop_seconds: float = 0
        self.loop_position: float = 0
        self.is_rec: bool = False

    def __str__(self):
        return f"CALL:{self.update_method}|L:{self.loop_seconds:05.2F}|" \
               f"P:{self.loop_position:.3F}|REC:{self.is_rec}"


class CollectionOwner(Generic[T]):
    """Class for list of items with index.
    It is a parent for SongPart, FileFinder
    It always has at least one element - never empty. """

    def __init__(self, first: T | list[T]):
        self.__items: list[T] = list()
        if type(first) == list:
            self.__items.extend(first)
        else:
            self.__items.append(first)
        if not self.__items:
            raise RuntimeError(f'Error: CollectionOwner init with empty collection')
        self.__idx: int = 0

    def get_idx(self, i: T = None) -> int:
        if i is None:
            return self.__idx
        elif i in self.__items:
            self.__idx = self.__items.index(i)
            return self.__idx
        else:
            self.__idx = self.item_count() - 1
            return -1

    def add_item(self, i: T) -> int:
        if i not in self.__items:
            self.__items.append(i)
        self.__idx = self.__items.index(i)
        return self.__idx

    def get_item(self) -> T:
        return self.__items[self.__idx]

    def set_item(self, i: int) -> T:
        self.__idx = i % len(self.__items)
        return self.__items[self.__idx]

    def item_count(self) -> int:
        return len(self.__items)

    def apply_to_each(self, method) -> None:
        for x in self.__items:
            method(x)

    def delete_selected(self) -> T | None:
        if self.item_count() <= 1:
            return None
        item = self.__items.pop(self.__idx)
        self.__idx = 0
        return item

    def get_str(self, next_idx: int = None) -> str:
        next_item = None
        if next_idx is not None:
            next_item = self.__items[next_idx % self.item_count()]
        item_sub_list = _stable_sub_list(self.__idx, self.__items, 5)
        curr_item = self.__items[self.__idx]
        result: str = ""
        for item in item_sub_list:
            if item == curr_item:
                result += f"*{item}\n"
            elif item == next_item:
                result += f"~{item}\n"
            else:
                result += f"-{item}\n"

        return result[:-1]

    def iterate(self, steps: int = 1) -> None:
        self.__idx += steps
        self.__idx %= self.item_count()


class FileFinder(CollectionOwner[str]):
    def __init__(self, dname: str, is_file: bool, end_with: str):
        assert os.path.isdir(dname)
        self.__end_with: str = end_with
        self.__dir: str = dname
        self.__is_file = is_file

        lst: list[str] = [x for x in filter(self.__match, os.listdir(self.__dir))]
        lst.sort(key=lambda x: os.path.getmtime(self.__dir + os.sep + x))

        if not lst:
            lst.append("")

        CollectionOwner.__init__(self, lst)

    def __match(self, f: str) -> bool:
        match1 = self.__is_file == os.path.isfile(self.__dir + os.sep + f)
        match2 = f.endswith(self.__end_with)
        return match1 and match2

    def get_dir(self) -> str:
        return self.__dir

    def get_full_name(self) -> str:
        return os.path.join(self.__dir, self.get_item())

    def get_end_with(self) -> str:
        return self.__end_with

    def delete_selected(self) -> T | None:
        path = self.get_full_name()
        deleted = super().delete_selected()
        if deleted and os.path.isfile(path):
            os.remove(path)
        return deleted


class EuclidSlicer:
    """ Spaces beats in steps in most even way.
    Used in Euclid drum patterns or when need to divide list almost evely into sub lists """

    def __init__(self, steps: int, beats: int, shift: int, accent: int = 0):
        assert steps and beats
        beats = min(beats, steps)
        shift %= steps
        dist: float = steps / beats  # exact distance between beats
        self._beat_steps: list[int] = [round(k * dist) for k in range(beats)]
        self._beat_steps = [(-shift + k) % steps for k in self._beat_steps]
        self._beats: int = beats
        self._steps: int = steps
        self._shift: int = shift
        self._accent: int = accent

    def get_ptrn_str(self) -> str:
        pattern_lst = ['.'] * self._steps
        for k in self._beat_steps:
            is_accent = self._accent > 0 and k % self._accent == 0
            pattern_lst[k] = '*' if is_accent else '+'
        return ''.join(pattern_lst)

    def beat_steps(self) -> list[int]:
        return self._beat_steps

    def sub_list_by_idx(self, idx: int) -> list[int]:
        return list(range(self._steps))[self.slice_by_idx(idx)]

    def slice_by_idx(self, idx: int) -> slice:
        idx %= self._beats
        idx_nxt = (idx + 1) % self._beats
        if self._beat_steps[idx] > self._beat_steps[idx_nxt]:
            return slice(self._beat_steps[idx], None)
        else:
            return slice(self._beat_steps[idx], self._beat_steps[idx_nxt])

    def __str__(self):
        return f"{self._steps},{self._beats},{self._shift}: {self.get_ptrn_str()}"


if __name__ == "__main__":
    def test_1():
        lst = list(range(22))
        sub_lst = _stable_sub_list(20, lst, 5)
        assert [20, 21, 0, 1, 2] == sub_lst
        print(sub_lst)


    test_1()
