import numpy as np

from utils.utilalsa import make_zero_buffer
from utils.utilconfig import MAX_LEN, SD_TYPE, SD_RATE
from utils.utillog import get_my_log
from utils.utilnumpy import copy_to_right, copy_to_left, vol_db, trim_buffer

my_log = get_my_log(__name__)


class WrapBuffer:
    """buffer that can wrap over the end when get/play and set/record samples """

    def __init__(self, sz: int = MAX_LEN):
        self.__is_reverse: bool = False
        self.__is_silent: bool = False
        self.__buff: np.ndarray = make_zero_buffer(sz)
        self.__info_str: str = ""
        self.__props_str: str = ""

    def __str__(self):
        if self.is_empty:
            return "---------------"
        if not self.__info_str:
            self.__info_str = f"V:{vol_db(self.__buff):03}db L:{len(self.__buff) / SD_RATE:05.2F}s"
        if not self.__props_str:
            self.__props_str = f"{'S' if self.__is_silent else ' '}{'R' if self.__is_reverse else ' '}"

        return self.__info_str + " " + self.__props_str

    def new_buff(self, sz: int = MAX_LEN) -> None:
        self.__buff = make_zero_buffer(sz)
        self.__info_str = ""

    def flip_reverse(self) -> None:
        self.__is_reverse = not self.__is_reverse
        self.__props_str = ""

    def flip_silent(self) -> None:
        self.__is_silent = not self.__is_silent
        self.__props_str = ""

    def set_silent(self, val: bool) -> None:
        self.__is_silent = val
        self.__props_str = ""

    @property
    def is_silent(self) -> bool:
        return self.__is_silent

    @property
    def length(self) -> int:
        return len(self.__buff)

    @property
    def is_empty(self) -> bool:
        return not (0 < len(self.__buff) < MAX_LEN)

    def multiply_buff(self, chg_factor: float) -> None:
        self.__buff = (self.__buff * chg_factor).astype(SD_TYPE)
        self.__info_str = ""

    def _record_samples(self, in_data: np.ndarray, idx: int) -> None:
        copy_to_left(self.__buff, in_data, idx)

    def play_samples(self, out_data: np.ndarray, idx: int, zero_buff: bool = False) -> None:
        if self.__is_silent:
            return
        tmp = self.__buff[::-1] if self.__is_reverse else self.__buff
        copy_to_right(tmp, out_data, idx, zero_buff)

    def finalize(self, idx: int, base_len: int, start_idx: int) -> None:
        """Trim is done only once to fix buffer length for empty loop.
        base_len - bigger of 2: parallel loop length or drum length
        case 1) base_len == 0 trim to idx value, bar length is NOT known yet
        case 2) base_len != 0 trim to multiple of base_len i.e.  1/4 1/2 1 2 3 ...
        """
        assert self.is_empty
        assert 0 <= start_idx < idx, f"start_idx: {start_idx}, idx: {idx}"
        self.__info_str = ""  # force recalculate volume and length
        if not base_len:  # Case 1
            assert start_idx == 0, "start==0 as we record 1st time"
            self.__buff = self.__buff[:idx]
        else:  # Case 2
            rec_len: int = idx - start_idx
            # new loop length must be ... 1/2, 1, 2, 3, ...
            save_base_len = base_len
            while rec_len < base_len // 2:
                base_len //= 2
            rec_len = round(rec_len / base_len) * base_len
            # align start with main loop if not started from zero
            offset = start_idx % base_len
            self.__buff = trim_buffer(self.__buff, rec_len, start_idx - offset)
            assert rec_len < save_base_len or rec_len % save_base_len == 0
            assert len(self.__buff) == rec_len
            assert rec_len % base_len == 0
            my_log.info(f"After trim length ratio: {rec_len / save_base_len}")
