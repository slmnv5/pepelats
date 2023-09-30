from __future__ import annotations

from math import log10

import numpy as np

from utils.utilconfig import MAX_SD_TYPE


def _calc_slices_lst(buff_len: int, data_len: int, idx: int) -> list[slice]:
    """Slices that wraps over the end of buffer making it a ring buffer. idx is where we start getting data"""
    if not buff_len or not data_len:
        return [slice(0, 0), slice(0, 0)]
    idx1 = idx % buff_len
    wrap_len = min(data_len, buff_len)
    idx2 = (idx + wrap_len) % buff_len
    if idx2 > idx1:
        return [slice(idx1, idx2), slice(0, idx2 - idx1)]
    else:
        to_buff_end: int = buff_len - idx1
        return [slice(idx1, buff_len), slice(0, idx2), slice(0, to_buff_end), slice(to_buff_end, to_buff_end + idx2)]


def copy_to_left(buff: np.ndarray, data: np.ndarray, idx: int) -> None:
    """ insert from data into buff starting with idx """
    buff_len = len(buff)
    data_len = len(data)
    slice_lst = _calc_slices_lst(buff_len, data_len, idx)
    if len(slice_lst) == 2:
        buff[slice_lst[0]] += data[slice_lst[1]]
    else:
        buff[slice_lst[0]] += data[slice_lst[2]]
        buff[slice_lst[1]] += data[slice_lst[3]]


def copy_to_right(buff: np.ndarray, data: np.ndarray, idx: int, zero_after: bool = False) -> None:
    """ insert from buff into data starting with idx.
    If zero_after=True empty buff after playing, this is needed for cyclical play of changing buffer """
    buff_len = len(buff)
    data_len = len(data)
    slice_lst = _calc_slices_lst(buff_len, data_len, idx)
    if len(slice_lst) == 2:
        data[slice_lst[1]] += buff[slice_lst[0]]
        if zero_after:
            buff[slice_lst[0]] = 0
    else:
        data[slice_lst[2]] += buff[slice_lst[0]]
        data[slice_lst[3]] += buff[slice_lst[1]]
        if zero_after:
            buff[slice_lst[0]] = 0
            buff[slice_lst[1]] = 0


def trim_buffer(buff: np.ndarray, new_len: int, new_start: int) -> np.ndarray:
    """ Trim ring buffer with wrap over the end """
    buff_len = len(buff)
    slice_lst = _calc_slices_lst(buff_len, new_len, new_start)
    if len(slice_lst) == 2:
        return buff[slice_lst[0]]
    else:
        return np.concatenate((buff[slice_lst[0]], buff[slice_lst[1]]), axis=0)


def vol_db(arr: np.ndarray) -> any:
    ratio = max(0.0001, np.max(arr, initial=0) / MAX_SD_TYPE)
    return round(20 * log10(ratio))
