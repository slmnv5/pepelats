import numpy as np

from utils.utilalsa import make_zero_buffer
from utils.utilconfig import MAX_LEN
from utils.utillog import get_my_log
from utils.utilnumpy import play_buffer, record_buffer, vol_db, trim_buffer

my_log = get_my_log(__name__)


class WrapBuffer:
    """buffer that can wrap over the end when get/play and set/record samples """

    def __init__(self, sz: int = MAX_LEN):
        self.__len_ratio: float = 0
        self.__is_reverse: bool = False
        self.__is_silent: bool = False
        self.__buff: np.ndarray = make_zero_buffer(sz)
        self.__info_str: str = ""
        self.__props_str: str = ""

    def init_str(self) -> None:
        self.__info_str, self.__props_str = "", ""

    def __str__(self):
        if self.is_empty:
            return "---------------"
        if not self.__info_str:
            self.__info_str = f"V:{vol_db(self.__buff):03}db"
            tmp: str
            if self.__len_ratio == 0:
                tmp = ""
            elif self.__len_ratio >= 1:
                tmp = f"{round(self.__len_ratio)}"
            else:
                tmp = f"1/{round(1 / self.__len_ratio)}"

            self.__info_str += tmp.rjust(5, " ")

        if not self.__props_str:
            self.__props_str = f" {'S' if self.__is_silent else ' '}{'R' if self.__is_reverse else ' '}"

        return self.__info_str + self.__props_str

    def max_buffer(self) -> None:
        self.__buff = make_zero_buffer(MAX_LEN)
        self.__info_str, self.__len_ratio = "", 0

    def flip_reverse(self) -> None:
        self.__is_reverse = not self.__is_reverse
        self.__props_str = ""

    def set_silent(self, val: bool) -> None:
        self.__is_silent = val
        self.__props_str = ""

    def is_silent(self) -> bool:
        return self.__is_silent

    @property
    def length(self) -> int:
        return len(self.__buff)

    @property
    def is_empty(self) -> bool:
        return not (0 < len(self.__buff) < MAX_LEN)

    def record_samples(self, in_data: np.ndarray, idx: int) -> None:
        record_buffer(self.__buff, in_data, idx)

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.__is_silent:
            return
        tmp = self.__buff[::-1] if self.__is_reverse else self.__buff
        play_buffer(tmp, out_data, idx)

    def finalize(self, idx: int, base_len: int, start_rec_idx: int) -> None:
        """Trim is done only once to fix buffer length for empty loop.
        base_len - bigger of 2: parallel loop length or 1 bar length
        case 1) base_len == 0 trim to idx value, bar length is NOT known yet
        case 2) base_len != 0 trim to multiple of base_len i.e.  1/4 1/2 1 2 3 ...
        """
        assert self.is_empty
        assert 0 <= start_rec_idx < idx, f"start_rec_idx: {start_rec_idx}, idx: {idx}"
        self.__info_str = ""  # force recalculate volume and length
        if not base_len:  # Case 1
            assert start_rec_idx == 0, "start==0 as we record 1st time"
            self.__buff = self.__buff[:idx]
            self.__len_ratio = 1
        else:  # Case 2
            rec_len: int = idx - start_rec_idx
            # new loop length must be ... 1/2, 1, 2, 3, ...
            tmp = base_len
            while rec_len < tmp // 2:
                tmp //= 2
            rec_len = round(rec_len / tmp) * tmp
            self.__len_ratio = rec_len / base_len
            # align start with main loop if not started from zero
            offset = start_rec_idx % tmp
            self.__buff = trim_buffer(self.__buff, rec_len, start_rec_idx - offset)

        my_log.info(f"After trim length ratio: {self.__len_ratio}")
