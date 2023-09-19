from __future__ import annotations

import os
from typing import TypeVar, Generic, Callable

T = TypeVar('T')


def _stable_sub_list(item: int, items: list[any], sub_list_size: int) -> list[any]:
    """ Sub list of elements surrounding item. If item changes sub list stays the same if
     item is still included in the sub list. Otherwise, all is recalculated."""
    lst_size = min(sub_list_size, len(items))
    start_id = (item // lst_size) * lst_size
    stop_id = start_id + lst_size
    if stop_id > lst_size:
        return items[start_id:] + items[: stop_id % lst_size]
    else:
        return items[start_id:stop_id]


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

    def selected_idx(self) -> int:
        return self.__idx

    def add_item(self, i: T) -> None:
        if i not in self.__items:
            self.__items.append(i)
        self.__idx = self.__items.index(i)

    def find_item_idx(self, i: T) -> int:
        if i in self.__items:
            return self.__items.index(i)
        return -1

    def select_idx(self, i: int) -> T:
        self.__idx = i % len(self.__items)
        return self.__items[self.__idx]

    def item_count(self) -> int:
        return len(self.__items)

    def selected_item(self) -> T:
        return self.__items[self.__idx]

    def apply_to_each(self, method) -> None:
        for x in self.__items:
            method(x)

    def delete_selected(self) -> T | None:
        if self.item_count() <= 1:
            return None
        item = self.__items.pop(self.__idx)
        self.__idx = 0
        return item

    def get_str(self, next_id: int = -1, method: Callable = None) -> str:
        next_item = None
        if 0 <= next_id < len(self.__items):
            next_item = self.__items[next_id]
        item_sub_list = _stable_sub_list(self.__idx, self.__items, 5)
        curr_item = self.__items[self.__idx]
        result: str = ""
        for item in item_sub_list:
            item_str = str(item) if method is None else method(item)
            if item == curr_item:
                result += f"*{item_str}\n"
            elif item == next_item:
                result += f"~{item_str}\n"
            else:
                result += f"-{item_str}\n"

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
        return os.path.join(self.__dir, self.selected_item())

    def get_end_with(self) -> str:
        return self.__end_with

    def delete_selected(self) -> T | None:
        path = self.get_full_name()
        deleted = super().delete_selected()
        if deleted and os.path.isfile(path):
            os.remove(path)
        return deleted


def euclid_spacing(steps: int, beats: int, shift: int) -> list[int]:
    """ Spaces beats in steps in most even way. Used in Euclid drum patterns """
    assert steps and beats
    beats = min(beats, steps)
    dist: float = steps / beats  # exact distance between beats
    beat_steps = [round(k * dist) for k in range(beats)]
    beat_steps = [(-shift + k) % steps for k in beat_steps]
    return beat_steps


def euclid_pattern_str(steps: int, beats: int, shift: int, accents: int) -> str:
    beat_steps = euclid_spacing(steps, beats, shift)
    lst = ['.'] * steps
    for k in beat_steps:
        lst[k] = '*' if accents > 0 and k % accents == 0 else '!'
    return "".join(lst)


def lst_for_slice(slc: int, length: int, slices: int) -> list[int]:
    """ Ex. slc = 1 for 3 slices in range(9) will be [3, 4, 5], Slices may have different sizes """
    lst = euclid_spacing(length, slices, 0)
    if slc > len(lst) - 1:
        slc = len(lst) - 1
    lst.append(length)
    return list(range(lst[slc], lst[slc + 1]))


def slice_for_elm(elm: int, length: int, slices: int) -> int:
    """ Ex. elm = 1 for 3 slices in range(9), it will be 0 as slice #0 is  [0, 1, 2] """
    elm = min(length - 1, elm)
    elm = max(0, elm)
    lst = euclid_spacing(length, slices, 0)
    for i in range(slices - 1):
        if lst[i] <= elm < lst[i + 1]:
            return i
    return slices - 1
