import os
import re
import subprocess
from typing import TypeVar, Generic, Iterable

from utils.utilconfig import HUGE_INT, SCR_ROWS, SCR_COLS

T = TypeVar('T')


def split_to_dict(data: str, bound: str, mark1: str, mark2: str,
                  strip1: str = "", strip2: str = "") -> dict[str, str]:
    """ split data into dictionary:
    bound mark1 <k> mark2 <v> bound mark1 <k> mark2 <v> bound ..... """
    result = dict()
    split_data = [x for x in data.split(bound) if mark1 in x and mark2 in x]
    for x in split_data:
        k, v = split_key_value(x, mark1, mark2, strip1, strip2)
        result[k] = v
    return result


def get_ip_address() -> str:
    if os.name == 'posix':
        result = subprocess.run(['hostname', '-I'], stdout=subprocess.PIPE)
        return result.stdout.decode()
    elif os.name == 'nt':
        result = subprocess.run(['ipconfig'], stdout=subprocess.PIPE)
        dic = split_to_dict(result.stdout.decode(), '\r\n', 'IPv4 Address', ': ', '. ')
        assert len(dic) == 1 and '' in dic
        return dic['']
    else:
        raise RuntimeError("OS must be posix or nt")


def split_key_value(data: str, mark1: str, mark2: str, strip1: str = "", strip2="") -> tuple[str, str]:
    """ Find 2 substrings using 2 markers and strip some chas from them
    Used to parse key-value pairs: mark1 k1 mark2 v1  mark1 k2 mark2 v2 """
    result = re.search(f'{mark1}(.*){mark2}(.*)', data)
    if result:
        return result.group(1).strip(strip1), result.group(2).strip(strip2)
    else:
        return "", ""


def _stable_sub_list(idx: int, items: list[any], sub_list_size: int) -> list[tuple[int, str]]:
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


class DrawInfo:
    def __init__(self):
        self.update_method: str = ""
        self.header: str = ""
        self.description: str = ""
        self.content: str = ""
        self.part_len: int = 0
        self.max_loop_len: int = 0
        self.idx: int = 0
        self.is_rec: bool = False

    def __str__(self):
        return f"CALL:{self.update_method}|L:{self.part_len}|" \
               f"P:{self.idx}|REC:{self.is_rec}"


class CollectionOwner(Generic[T]):
    """Class for list of items with index.
    It is a parent for SongPart, FileFinder
    It always has at least one element - never empty. """

    def __init__(self, first: T | Iterable[T]):
        self.__items: list[T] = list()
        if isinstance(first, Iterable):
            self.__items.extend(first)
        else:
            self.__items.append(first)
        if not self.__items:
            raise RuntimeError(f'Error: CollectionOwner init with empty collection')
        self.__idx: int = 0

    def get_list(self) -> list[T]:
        return self.__items

    def get_idx(self) -> int:
        return self.__idx

    def add_item(self, item: T) -> int:
        if item not in self.__items:
            self.__items.append(item)
        self.__idx = self.__items.index(item)
        return self.__idx

    def get_item(self) -> T:
        return self.__items[self.__idx]

    def select_idx(self, i: int) -> None:
        self.__idx = i % len(self.__items)

    def set_at_idx(self, i: int, item: T) -> None:
        i = i % len(self.__items)
        self.__items[i] = item

    def item_count(self) -> int:
        return len(self.__items)

    def delete_selected(self) -> T | None:
        if self.item_count() <= 1:
            return None
        item = self.__items.pop(self.__idx)
        self.__idx = 0
        return item

    def get_str(self, next_idx: int = None, pad_str: str = None) -> str:
        sub_list_sz: int = SCR_ROWS - 5
        item_sub_list = _stable_sub_list(self.__idx, self.__items, sub_list_sz)
        tmp: list[str] = list()
        for (k, s) in item_sub_list:
            if k == self.__idx:
                tmp.append(f"*{k:02} {s}")
            elif k == next_idx:
                tmp.append(f"~{k:02} {s}")
            else:
                tmp.append(f"-{k:02} {s}")
        if pad_str:
            tmp = [x.ljust(SCR_COLS, pad_str) for x in tmp]
        return '\n'.join(tmp)

    def iterate(self, steps: int) -> None:
        self.__idx += steps
        self.__idx %= self.item_count()


class FileFinder(CollectionOwner[str]):
    def __init__(self, dname: str, is_file: bool, end_with: str):
        assert os.path.isdir(dname)
        self.__end_with: str = end_with
        self.__dir: str = dname
        self.__is_file = is_file

        lst: list[str] = [x for x in os.listdir(self.__dir) if self.__match(x)]
        lst.sort()

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
        return ''.join(pattern_lst)

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
