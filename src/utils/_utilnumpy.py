# noinspection PyProtectedMember
from typing import Any
from typing import List

from typing import Tuple, Union


def calc_slices(buff_len: int, data_len: int, idx: int) -> Tuple[slice, Union[slice, None]]:
    assert 0 < data_len <= buff_len, f"Must be: 0 < data_len {data_len} <= buff_len {buff_len}"
    idx1 = idx % buff_len
    idx2 = (idx + data_len) % buff_len
    if idx2 > idx1:
        return slice(idx1, idx2), None
    else:
        return slice(idx1, buff_len), slice(0, idx2)


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
