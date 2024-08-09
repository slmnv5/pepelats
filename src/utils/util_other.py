import os
import re
from typing import TypeVar, Generic, Iterable, Callable, Any

T = TypeVar('T')

HUGE_INT = 2 ** 32 - 1


def split_to_dict(data: str, bound: str, mark1: str, mark2: str,
                  strip1: str = "", strip2: str = "") -> dict[str, str]:
    """ split string with bounds and markers into dictionary:
    bound mark1 <k1> mark2 <v1> bound mark1 <k2> mark2 <v2> bound mark1 ..... """
    result = dict()
    split_data = [x for x in data.split(bound) if mark1 in x and mark2 in x]
    for x in split_data:
        k, v = split_key_value(x, mark1, mark2, strip1, strip2)
        result[k] = v
    return result


def split_key_value(data: str, mark1: str, mark2: str, strip1: str = "", strip2: str = "") -> tuple[str, str]:
    """ Find 2 substrings using 2 markers and 2 strips.
    Used to parse key-value pairs: mark1 <k> mark2 <v>  """
    result = re.search(f'{mark1}(.*?){mark2}(.*)', data, re.DOTALL)
    if result:
        return result.group(1).strip(strip1), result.group(2).strip(strip2)
    else:
        return "", ""


def _stable_sub_list(idx: int, items: list[Any], sub_list_size: int) -> list[tuple[int, Any]]:
    """ Sub list of elements surrounding one item at position = idx.
    If item's idx changes sub list stays the same if item is still included in the sub list.
    Otherwise, new sub list including item returned """
    items_len: int = len(items)
    lst_size: int = min(sub_list_size, items_len)
    start_idx: int = (idx // lst_size) * lst_size
    stop_idx: int = start_idx + lst_size
    if stop_idx < items_len:
        tmp: list[int] = [*range(start_idx, stop_idx)]
    else:
        tmp: list[int] = [*range(start_idx, items_len), *range(0, stop_idx % items_len)]

    return [(k, items[k]) for k in tmp]


class CollectionOwner(Generic[T]):
    """Class for list of items with index.
    It is used for SongPart, Song, FileFinder
    May be empty and throw exceptions """

    def __init__(self, t: T | Iterable[T]):
        self.__items: list[T] = list()
        if isinstance(t, Iterable):
            self.__items.extend(t)
        else:
            self.__items.append(t)
        if self.item_count() == 0 or None in self.__items:
            raise RuntimeError("Empty CollectionOwner class")
        self.__idx: int = 0

    def get_generic_type(self) -> type:
        return self.__orig_class__.__args__[0]  # type: ignore

    def is_type_ok(self, x: Any) -> bool:
        return isinstance(x, self.get_generic_type())

    def get_first(self) -> T:
        return self.__items[0]

    def get_idx(self) -> int:
        return self.__idx

    def add_item(self, item: T) -> int:
        assert self.is_type_ok(item), f"{type(item)} type is not correct"
        if item not in self.__items:
            self.__items.append(item)
        self.__idx = self.__items.index(item)
        return self.__idx

    def get_item(self) -> T:
        return self.__items[self.__idx]

    def select_idx(self, i: int) -> T:
        self.__idx = i % len(self.__items)
        return self.__items[self.__idx]

    def for_each(self, act: Callable[[T], Any]) -> None:
        for x in [x for x in self.__items]:
            act(x)

    def item_count(self) -> int:
        return len(self.__items)

    def delete_item(self) -> T:
        if self.item_count() <= 1:
            return None
        item = self.__items.pop(self.__idx)
        self.__idx = 0
        return item

    def get_str(self, rows: int, next_idx: int = None) -> str:
        sub_list = _stable_sub_list(self.__idx, self.__items, rows)
        tmp: list[str] = list()
        for (k, s) in sub_list:
            if k == self.__idx:
                tmp.append(f"*{k:02} {s}")
            elif k == next_idx:
                tmp.append(f"~{k:02} {s}")
            else:
                tmp.append(f"-{k:02} {s}")
        return '\n'.join(tmp)

    def get_next(self) -> T:
        self.__idx += 1
        self.__idx %= self.item_count()
        return self.__items[self.__idx]

    def get_prev(self) -> T:
        self.__idx += -1
        self.__idx %= self.item_count()
        return self.__items[self.__idx]


class FileFinder:
    def __init__(self, dname: str, is_file: bool, end_with: str):
        assert os.path.isdir(dname)
        self.__end_with: str = end_with
        self.__dir: str = dname
        self.__is_file = is_file

        lst: list[str] = [x for x in os.listdir(self.__dir) if self.__match(x)]
        lst.sort()

        if not lst:
            lst.append("")

        self._co = CollectionOwner[str](lst)

    def __match(self, f: str) -> bool:
        match1 = self.__is_file == os.path.isfile(self.__dir + os.sep + f)
        match2 = f.endswith(self.__end_with)
        return match1 and match2

    def get_dir(self) -> str:
        return self.__dir

    def get_full_name(self) -> str:
        return os.path.join(self.__dir, self._co.get_item())

    def get_end_with(self) -> str:
        return self.__end_with

    def delete_item(self) -> T:
        path = self.get_full_name()
        deleted = self._co.delete_item()
        if deleted and os.path.isfile(path):
            os.remove(path)
        return deleted

    def get_item(self) -> str:
        return self._co.get_item()

    def get_str(self, param) -> str:
        return self._co.get_str(param)

    def add_item(self, param) -> int:
        return self._co.add_item(param)

    def item_count(self) -> int:
        return self._co.item_count()

    def get_prev(self) -> str:
        return self._co.get_prev()

    def get_next(self) -> str:
        return self._co.get_next()


class EuclidSlicer:
    """ Arrange beats in given number of steps in most even way.
    Used in Euclid drum patterns or when dividing list most evenly into sub lists """

    def __init__(self, steps: int, beats: int, shift: int, accent: int):
        assert steps and beats
        beats = min(beats, steps)
        shift %= steps
        # array of steps with beats
        self._beat_steps: list[int] = [round(k * steps / beats) for k in range(beats)]
        # same array shifted
        self._beat_steps = [(-shift + k) % steps for k in self._beat_steps]
        self._steps: int = steps  # steps in pattern
        self._beats: int = beats  # beats in pattern
        self._shift: int = shift  # shift of 1-st beat
        self._accent: int = accent if accent > 0 else HUGE_INT  # every N-th step is accented

    def get_ptrn_str(self) -> str:
        pattern_lst = ['.'] * self._steps
        for k in self._beat_steps:
            is_accent = k % self._accent == 0
            pattern_lst[k] = '*' if is_accent else '+'
        return "".join(pattern_lst)

    def beat_steps(self) -> list[int]:
        return self._beat_steps

    def sub_list_by_idx(self, idx: int) -> list[int]:
        """ get sub list that contains idx """
        sl: slice = self.slice_by_idx(idx)
        return list(range(sl.start, sl.stop))

    def slice_by_idx(self, idx: int) -> slice:
        """ find slice for sub list that contains idx """
        idx %= self._beats
        idx_nxt = (idx + 1) % self._beats
        if self._beat_steps[idx] > self._beat_steps[idx_nxt]:
            return slice(self._beat_steps[idx], self._steps, 1)
        else:
            return slice(self._beat_steps[idx], self._beat_steps[idx_nxt], 1)

    def __str__(self):
        return f"{self._steps},{self._beats},{self._shift}: {self.get_ptrn_str()}"


if __name__ == "__main__":
    pass
