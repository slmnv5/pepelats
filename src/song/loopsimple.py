from threading import Event, Timer

import numpy as np
import sounddevice as sd

from drum.basedrum import BaseDrum
from song.wrapbuffer import WrapBuffer
from utils.util_other import HUGE_INT


class LoopState:
    # 5k ~ 0.1 second. May be late by this time without waiting for next bar start.
    LATE_SAMPLES: int = 5000

    def __init__(self):
        self.rec: bool = False
        self.stop_len: int = 0
        self.stop_event: Event = Event()
        self.idx: int = 0  # idx for audio buffer
        self.start_idx: int = 0  # start of recording, used in sub class


class LoopSimple(WrapBuffer):
    """Loop truncates itself to be multiple of bar length. Bar length is stored in a drum.
    Drum is passed as parameter to play_loop()  """
    _state: LoopState = LoopState()

    def __init__(self, size: int = None, buff: np.ndarray = None):
        WrapBuffer.__init__(self, size, buff)
        self._info_str: str = ""
        self.stop_never()

    def get_index(self) -> int:
        return self._state.idx

    def rec_on(self) -> None:
        self._state.rec = True

    def rec_off(self) -> None:
        self._state.rec = False

    def is_rec(self) -> bool:
        return self._state.rec

    def get_base_len(self, drum: BaseDrum) -> int:
        return drum.get_bar_len()

    def trim_buffer(self, idx: int, base_len: int) -> None:
        """trims buffer length to multiple of base_len.
        base_len is length of bar """
        self._trim(idx, base_len)

    def play_loop(self, drum: BaseDrum):
        self._state.idx, self._state.start_idx = 0, 0
        self.stop_never()
        if self.is_empty():
            self._state.rec = True

        # noinspection PyUnusedLocal
        def callback(in_data, out_data, frame_count, time_info, status):
            out_data[:] = 0
            drum.play(out_data, self._state.idx)
            self.play(out_data, self._state.idx)

            if self._state.rec:
                self._record(in_data, self._state.idx)

            self._state.idx += frame_count
            if self._state.idx >= self._state.stop_len:
                self._state.stop_event.set()

        with sd.Stream(callback=callback):
            self._state.stop_event.wait()

        # if loop is empty will trim to correct size
        if self.is_empty():
            base_len: int = self.get_base_len(drum)
            self.trim_buffer(self._state.idx, base_len)
            if not base_len:
                Timer(1.0, drum.set_bar_len, [self._state.idx]).start()

        self._state.rec = False

    def stop_never(self) -> None:
        self._state.stop_len = HUGE_INT
        self._state.stop_event.clear()

    def stop_at_bound(self, bound_value: int) -> None:
        over: int = self._state.idx % bound_value if bound_value else 0
        if over < LoopState.LATE_SAMPLES:
            self._state.stop_len = 0
            self._state.stop_event.set()
        else:
            self._state.stop_len = self._state.idx + (bound_value - over)

    def __str__(self):
        if self.is_empty():
            return "-" * 15
        if not self._info_str:
            self._info_str = f"{self.get_decibel()} {self.get_seconds()}"

        return f"{self._info_str} {self.get_state()}"
