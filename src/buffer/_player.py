import sounddevice as sd

from buffer._wrapbuffer import WrapBuffer
from buffer._oneloopctrl import OneLoopCtrl
from drum.basedrum import SimpleDrum

from utils.utilconfig import MAX_LEN
import logging


class Player(WrapBuffer):
    """Abstract class that can play record using sounddevice"""

    def __init__(self, ctrl: OneLoopCtrl, length: int = MAX_LEN):
        WrapBuffer.__init__(self, length)
        self._ctrl: OneLoopCtrl = ctrl

    def get_drum(self) -> SimpleDrum:
        return self._ctrl.get_drum()

    def set_ctrl(self, ctrl: OneLoopCtrl) -> None:
        self._ctrl = ctrl

    def play_buffer(self):
        logging.debug(f"===Start {self.__class__.__name__}")

        # noinspection PyUnusedLocal
        def callback(in_data, out_data, frame_count, time_info, status):

            out_data[:] = 0
            assert len(out_data) == len(in_data) == frame_count
            self._play_samples(out_data, self._ctrl.idx)

            if self._ctrl.get_is_rec():
                self._record_samples(in_data, self._ctrl.idx)

            self._ctrl.idx += frame_count
            if self._ctrl.idx >= self._ctrl.get_stop_len():
                self._ctrl.stop_at_bound(0)

        with sd.Stream(callback=callback):
            self._ctrl.get_stop_event().wait()

        if self.is_empty:
            self.trim_buffer()

        logging.debug(f"===Stop {self.__class__.__name__}")

    def trim_buffer(self) -> None:
        """trim buffer to the length at stop event = idx. Overridden by child class"""
        idx: int = self._ctrl.idx
        logging.debug(f"trim_buffer {self.__class__.__name__} idx {idx}")
        self.finalize(idx, 0)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle some fields
        del state["_ctrl"]
        return state
