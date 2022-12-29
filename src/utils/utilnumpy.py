# noinspection PyProtectedMember
from typing import Any
from typing import List

from typing import Tuple, Union

import numpy as np

from utils.utilalsa import IN_CH


def calc_slices(buff_len: int, data_len: int, idx: int) -> Tuple[slice, Union[slice, None]]:
    assert 0 < data_len <= buff_len, f"Must be: 0 < data_len {data_len} <= buff_len {buff_len}"
    idx1 = idx % buff_len
    idx2 = (idx + data_len) % buff_len
    if idx2 > idx1:
        return slice(idx1, idx2), None
    else:
        return slice(idx1, buff_len), slice(0, idx2)


def record_sound_buff(buff: np.ndarray, data: np.ndarray, idx: int) -> None:
    """ insert data into buff starting with idx """
    assert buff.ndim == data.ndim
    data_len = len(data)
    if IN_CH == 1:
        data = np.broadcast_to(data, (data_len, 2))
    slice1, slice2 = calc_slices(len(buff), data_len, idx)
    if slice2 is None:
        buff[slice1] += data[:]
    else:
        s1 = slice1.stop - slice1.start
        s2 = slice2.stop - slice2.start
        buff[slice1] += data[0:s1]
        buff[slice2] += data[s1:s1 + s2]


def play_sound_buff(buff: np.ndarray, data: np.ndarray, idx: int) -> None:
    """ insert buff into data starting with idx """
    assert type(buff) == type(data), f"{type(buff)}, {type(data)}"
    assert buff.ndim == data.ndim
    data_len = len(data)
    slice1, slice2 = calc_slices(len(buff), data_len, idx)
    if slice2 is None:
        data[:] += buff[slice1]
    else:
        s1 = slice1.stop - slice1.start
        data[:s1] += buff[slice1]
        data[s1:] += buff[slice2]


def get_stable_list(item: int, items: List[Any], max_size: int) -> Tuple[List[Any], List[int]]:
    """ Sub list of items around item, if item changes list stay the same if item is still included
     otherwise recalculated. List of item indexes is also returned """
    idxs = list(range(0, len(items)))
    lst_size = min(max_size, len(items))
    start_id = (item // lst_size) * lst_size
    stop_id = start_id + lst_size
    if stop_id > lst_size:
        return items[start_id:] + items[: stop_id % lst_size], idxs[start_id:] + idxs[: stop_id % lst_size]
    else:
        return items[start_id:stop_id], idxs[start_id:stop_id]
