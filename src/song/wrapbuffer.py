import numpy as np

from utils.util_audio import correct_sound, AUDIO_INFO
from utils.util_log import MY_LOG
from utils.util_numpy import from_buff_to_data, from_data_to_buff, trim_buffer


class WrapBuffer:
    """ Buffer that can wrap over the end when get/play and set/record samples.
    if length == MAX_LEN it is empty.
    Another length indicates that it was recorded and trimmed to proper length.
    """

    def __init__(self, size: int = None, buff: np.ndarray = None):
        if buff is not None and size is not None:
            raise ValueError("WrapBuffer init got 2 parameters")
        elif buff is not None:
            if len(buff) > AUDIO_INFO.MAX_LEN:
                raise ValueError(f"WrapBuffer init size is too big")
            self.__buff = buff
        elif size is not None:
            self.__buff: np.ndarray = AUDIO_INFO.get_zero_buffer(size)
        else:
            self.__buff: np.ndarray = AUDIO_INFO.get_zero_buffer(AUDIO_INFO.MAX_LEN)

        self.__is_reverse: bool = False
        self.__is_silent: bool = False

    def get_buff(self) -> np.ndarray:
        return self.__buff

    def set_buff(self, buff: np.ndarray) -> None:
        self.__buff = buff

    def get_decibel(self) -> str:
        return f"V:{AUDIO_INFO.vol_db(self.__buff):03}db"

    def get_seconds(self) -> str:
        return f"L:{(self.get_len() / AUDIO_INFO.SD_RATE): 04.1F}s"

    def get_state(self) -> str:
        return f" {'S' if self.__is_silent else ' '}{'R' if self.__is_reverse else ' '}"

    def correct_buffer(self) -> None:
        self.__buff = correct_sound(self.__buff, AUDIO_INFO.SD_CH, AUDIO_INFO.SD_TYPE)

    def flip_reverse(self) -> None:
        self.__is_reverse = not self.__is_reverse

    def set_silent(self, is_silent: bool) -> None:
        self.__is_silent = is_silent

    def is_silent(self) -> bool:
        return self.__is_silent

    def max_buffer(self) -> None:
        """ make it max length, as if it is empty """
        self.__buff = AUDIO_INFO.get_zero_buffer(AUDIO_INFO.MAX_LEN)

    def get_len(self) -> int:
        return len(self.__buff)

    def is_empty(self) -> bool:
        return len(self.__buff) >= AUDIO_INFO.MAX_LEN

    def _record(self, in_data: np.ndarray, idx: int) -> None:
        from_data_to_buff(self.__buff, in_data, idx, True)

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self.__is_silent:
            return
        tmp = self.__buff[::-1] if self.__is_reverse else self.__buff
        from_buff_to_data(tmp, out_data, idx)

    def _trim(self, idx: int, base_len: int, start_idx: int = 0) -> None:
        """Trim is done only once to fix buffer length for empty loop.
        base_len - longest parallel loop or a drum
        case 1) base_len == 0 trim to idx value, drum length is NOT known yet, strat_idx == 0
        case 2) base_len != 0 trim to multiple of base_len i.e.  1/4 1/2 1 2 3 ...
        if start_idx > 0 - record started not from 0, account for this
        """
        if len(self.__buff) != AUDIO_INFO.MAX_LEN:
            raise RuntimeError(f"Trimming buffer that is not empty")
        if not 0 <= base_len < AUDIO_INFO.MAX_LEN:
            raise RuntimeError(f"Trimming base_len is not correct: {base_len}")
        if not (0 <= start_idx < idx):
            raise RuntimeError(f"Trimming idx=={idx} and start_idx=={start_idx} are not correct")
        if not base_len:  # Case 1
            if start_idx:
                raise RuntimeError(f"Trimming start_idx=={start_idx}, it must be zero when base_len is zero")
            self.__buff = self.__buff[:idx]
            len_ratio = 1
        else:  # Case 2
            start_idx -= start_idx % base_len  # set start_idx at multiple of base_len
            record_len = idx - start_idx
            # new length must be ... 1/2, 1, 2, 3, ... of base_len
            tmp = base_len
            while record_len < tmp:
                tmp //= 2
            new_len: int = round(record_len / tmp) * tmp
            assert new_len >= tmp > 0
            len_ratio: float = new_len / base_len
            self.__buff = trim_buffer(self.__buff, new_len, start_idx)
        MY_LOG.info(f"After trim length ratio: {len_ratio}")
