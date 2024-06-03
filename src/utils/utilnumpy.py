

import numpy as np


def _calc_slices_lst(buff_len: int, data_len: int, buff_idx: int) -> list[slice]:
    """Slices that wraps over the end of buffer making it a ring buffer. buff_idx is where we start getting data"""
    if not buff_len or not data_len:
        return [slice(0, 0), slice(0, 0)]
    idx1 = buff_idx % buff_len
    wrap_len = min(data_len, buff_len)
    idx2 = (buff_idx + wrap_len) % buff_len
    if idx2 > idx1:
        return [slice(idx1, idx2), slice(0, idx2 - idx1)]
    else:
        to_buff_end: int = buff_len - idx1
        return [slice(idx1, buff_len), slice(0, idx2), slice(0, to_buff_end), slice(to_buff_end, to_buff_end + idx2)]


def from_data_to_buff(buff: np.ndarray, data: np.ndarray, buff_idx: int) -> None:
    """ insert from data into buff starting with idx """
    buff_len = len(buff)
    data_len = len(data)
    slice_lst = _calc_slices_lst(buff_len, data_len, buff_idx)
    if len(slice_lst) == 2:
        buff[slice_lst[0]] += data[slice_lst[1]]
    else:
        buff[slice_lst[0]] += data[slice_lst[2]]
        buff[slice_lst[1]] += data[slice_lst[3]]


def from_buff_to_data(buff: np.ndarray, data: np.ndarray, buff_idx: int) -> None:
    """ insert from buff into data starting with idx """
    buff_len = len(buff)
    data_len = len(data)
    slice_lst = _calc_slices_lst(buff_len, data_len, buff_idx)
    if len(slice_lst) == 2:
        data[slice_lst[1]] += buff[slice_lst[0]]
    else:
        data[slice_lst[2]] += buff[slice_lst[0]]
        data[slice_lst[3]] += buff[slice_lst[1]]


def trim_buffer(buff: np.ndarray, new_len: int, buff_idx: int) -> np.ndarray:
    """ Trim ring buffer with wrap over the end, new start is at buff_idx """
    buff_len = len(buff)
    slice_lst = _calc_slices_lst(buff_len, new_len, buff_idx)
    if len(slice_lst) == 2:
        return buff[slice_lst[0]]
    else:
        return np.concatenate((buff[slice_lst[0]], buff[slice_lst[1]]), axis=0)
