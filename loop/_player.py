from abc import abstractmethod

import numpy as np
import sounddevice as sd

import logging
from loop._oneloopctrl import OneLoopCtrl


class Player:
    """Abstract class that can play record using sounddevice"""

    def __init__(self, ctrl: OneLoopCtrl):
        self._ctrl: OneLoopCtrl = ctrl

    def set_ctrl(self, ctrl: OneLoopCtrl) -> None:
        self._ctrl = ctrl

    def play_buffer(self):
        logging.debug(f"===Start {self.__class__.__name__}")

        # noinspection PyUnusedLocal
        def callback(in_data, out_data, frame_count, time_info, status):

            out_data[:] = 0
            assert len(out_data) == len(in_data) == frame_count
            self.play_samples(out_data, self._ctrl.idx)

            if self._ctrl.is_rec:
                self.record_samples(in_data, self._ctrl.idx)

            self._ctrl.idx += frame_count
            if self._ctrl.idx >= self._ctrl.get_stop_len():
                self._ctrl.stop_at_bound(0)

        with sd.Stream(callback=callback):
            self._ctrl.get_stop_event().wait()

        if self.is_empty:
            self.trim_buffer(self._ctrl.idx)

        logging.debug(f"===Stop {self.__class__.__name__}")

    @abstractmethod
    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        pass

    @abstractmethod
    def record_samples(self, in_data: np.ndarray, idx: int) -> None:
        pass

    @abstractmethod
    def trim_buffer(self, idx: int) -> None:
        pass

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        pass

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle some fields
        del state["_ctrl"]
        return state
