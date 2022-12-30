import logging

import numpy as np

from utils.utilalsa import make_zero_buffer
from utils.utilconfig import MAX_LEN, SD_MAX, SD_TYPE
from utils.utilnumpy import play_sound_buff, record_sound_buff


class WrapBuffer:
    """buffer that can wrap over the end when get and set data. Can undo, redo"""

    def __init__(self, length: int = MAX_LEN):
        self.__volume: float = 0
        self.__is_reverse: bool = False
        self.__is_silent: bool = False
        self.__buff: np.ndarray = make_zero_buffer(length)
        self.__start: int = -1
        self._buffer_str: str = ""

    def flip_reverse(self):
        self.__is_reverse = not self.__is_reverse
        self._buffer_str = ""

    def flip_silent(self):
        self.__is_silent = not self.__is_silent
        self._buffer_str = ""

    @property
    def length(self) -> int:
        return len(self.__buff)

    @property
    def volume(self) -> float:
        if not self.__volume:
            self.__volume = np.max(self.__buff) / SD_MAX
        return self.__volume

    def _show_properties(self) -> str:
        return f"{'S' if self.__is_silent else ' '}{'R' if self.__is_reverse else ' '}"

    @property
    def is_empty(self) -> bool:
        return len(self.__buff) == MAX_LEN

    def zero_buff(self) -> None:
        self.__buff[:] = 0
        self._buffer_str = ""
        self.__volume = 0

    def multiply_buff(self, chg_factor: float) -> None:
        self.__buff = (self.__buff * chg_factor).astype(SD_TYPE)
        self._buffer_str = ""
        self.__volume = 0

    def resize_buff(self, length: int) -> None:
        diff = length - len(self.__buff)
        if diff > 0:
            self.__buff = np.concatenate((self.__buff, make_zero_buffer(diff)), axis=0)
        elif diff < 0:
            self.__buff = self.__buff[0, length]
        self._buffer_str = ""

    def _record_samples(self, in_data: np.ndarray, idx: int) -> None:
        """Record and fix start for empty, recalculate volume for non empty"""
        if self.is_empty:
            if self.__start < 0:
                self.__start = idx
        record_sound_buff(self.__buff, in_data, idx)

    def _play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if self.__is_silent:
            return
        tmp = self.__buff[::-1] if self.__is_reverse else self.__buff
        play_sound_buff(tmp, out_data, idx)

    def finalize(self, idx: int, trim_len: int) -> None:
        """Trim is called once to fix buffer length. Buffer must be multiple of trim_len.
         If trim_len == 0 make buffer == idx value"""
        if not self.is_empty:
            raise RuntimeError("finalize: buffer must be empty")
        if self.__start < 0:
            raise RuntimeError("finalize: start is negative, recording did not start")

        if trim_len <= 0:
            assert self.__start == 0, "start must be zero"
            self.__buff = self.__buff[:idx]
            return

        rec_len: int = idx - self.__start
        assert rec_len > 0, "idx must be bigger than start"
        while rec_len < trim_len // 2:
            trim_len = trim_len // 2

        rec_len = round(rec_len / trim_len) * trim_len
        if rec_len == 0:
            rec_len += trim_len
        # rec_len is multiple of trim_len: .. 1/8, 1/4, 1/2, 1, 2, 3, ...
        # align start with main loop's trim_len
        offset: int = idx % trim_len
        if offset < trim_len // 2:
            self.__start -= offset
        else:
            self.__start += (trim_len - offset)

        assert self.__start >= 0

        new_buff = make_zero_buffer(rec_len)
        play_sound_buff(self.__buff, new_buff, self.__start)
        self.__buff = new_buff

        logging.debug(f"after trim: len {len(self.__buff)} trim_len {trim_len} start {self.__start} idx {idx}")
        assert self.length % trim_len == 0 and self.length > 0, "incorrect buffer trim"
        self._buffer_str = ""


if __name__ == "__main__":
    pass
