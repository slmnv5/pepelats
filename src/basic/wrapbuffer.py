import numpy as np

from basic.audioinfo import correct_sound, AudioInfo
from utils.utillog import MyLog
from utils.utilnumpy import from_buff_to_data, from_data_to_buff


class WrapBuffer:
    """buffer that can wrap over the end when get/play and set/record samples """

    def __init__(self, sz: int = AudioInfo().MAX_LEN):
        if not (0 < sz <= AudioInfo().MAX_LEN):
            raise RuntimeError(f"Buffer size is not correct: {sz}")
        self.__is_reverse: bool = False
        self.__is_silent: bool = False
        self.__buff: np.ndarray = np.zeros((sz, AudioInfo().SD_CH), AudioInfo().SD_TYPE)
        self.__info_str: str = ""
        self.__props_str: str = ""

    def __str__(self):
        if self.is_empty:
            return ""
        if not self.__info_str:
            self.__info_str = f"V:{AudioInfo().vol_db(self.__buff):02}db L:{(self.get_len() / AudioInfo().SD_RATE):04.1F}s "
        if not self.__props_str:
            self.__props_str = f" {'S' if self.__is_silent else ' '}{'R' if self.__is_reverse else ' '}"

        return self.__info_str + self.__props_str

    def correct_buffer(self) -> None:
        self.__buff = correct_sound(self.__buff, AudioInfo().SD_CH, AudioInfo().SD_TYPE)

    def flip_reverse(self) -> None:
        self.__is_reverse = not self.__is_reverse
        self.__props_str = ""

    def set_silent(self, val: bool) -> None:
        self.__is_silent = val
        self.__props_str = ""

    def is_silent(self) -> bool:
        return self.__is_silent

    def max_buffer(self) -> None:
        shape = self.__buff.shape
        assert len(shape) == 2
        tmp = np.zeros((AudioInfo().MAX_LEN, shape[1]), self.__buff.dtype)
        tmp[:shape[0]] = self.__buff[:shape[0]]
        self.__buff = tmp

    def get_len(self) -> int:
        return len(self.__buff)

    @property
    def is_empty(self) -> bool:
        return not (0 < len(self.__buff) < AudioInfo().MAX_LEN)

    def record(self, in_data: np.ndarray, idx: int) -> None:
        from_data_to_buff(self.__buff, in_data, idx, True)

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self.__is_silent:
            return
        tmp = self.__buff[::-1] if self.__is_reverse else self.__buff
        from_buff_to_data(tmp, out_data, idx)

    def finalize(self, idx: int, base_len: int) -> None:
        """Trim is done only once to fix buffer length for empty loop.
        base_len - bigger of 2: parallel loop length or 1 bar length
        case 1) base_len == 0 trim to idx value, bar length is NOT known yet
        case 2) base_len != 0 trim to multiple of base_len i.e.  1/4 1/2 1 2 3 ...
        """
        assert self.is_empty
        if not base_len:  # Case 1
            self.__buff = self.__buff[:idx]
            len_ratio = 1
        else:  # Case 2
            # new loop length must be ... 1/2, 1, 2, 3, ...
            tmp = base_len
            while idx < tmp // 2:
                tmp //= 2
            idx = round(idx / tmp) * tmp
            len_ratio = idx / base_len
            self.__buff = self.__buff[:idx]

        MyLog().info(f"After trim length ratio: {len_ratio}")
