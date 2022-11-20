import logging
from threading import Timer

import numpy as np

from drum import RealDrum
from loop._oneloopctrl import OneLoopCtrl
from loop._player import Player
from utils import MAX_LEN


class LoopSimple(Player):
    """Loop truncate itself to be multiple of drum if drum is ready.
    Or init drum of correct length if drum is empty"""

    def __init__(self, ctrl: OneLoopCtrl, length: int = MAX_LEN):
        super().__init__(ctrl, length)

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self.get_drum().play_samples(out_data, idx)
        super().play_samples(out_data, idx)

    def trim_buffer(self) -> None:
        """create drums of correct length if drum is empty,
        otherwise trims self.length to multiple of drum length"""
        idx: int = self._ctrl.idx
        logging.debug(f"trim_buffer {self.__class__.__name__} idx {idx}")
        if not self.get_drum().get_length():
            self.get_drum().prepare_drum(idx)
            self.finalize(idx, 0)
        else:
            self.finalize(idx, self.get_drum().get_length())

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle some fields
        del state["_ctrl"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Add _ctrl missing in the pickle
        self._ctrl = None

    def __str__(self):
        if not self.get_drum().get_length() or self.is_empty:
            return "---------"
        if not self._str:
            self._str = f"L:{self.length // self.get_drum().get_length():02} V:{self.volume:02} " \
                        f"{self._show_properties()}"
        return self._str


if __name__ == "__main__":
    def test1():
        c1 = OneLoopCtrl(RealDrum())
        c1._is_rec = True
        Timer(2, c1.stop_at_bound, args=[0]).start()
        l1 = LoopSimple(c1)
        l1.play_buffer()
        c1.get_stop_event().clear()
        Timer(3, c1.stop_at_bound, args=[0]).start()
        l1.play_buffer()


    def test2():
        c1 = OneLoopCtrl(RealDrum())
        c1._is_rec = True
        Timer(3.9, c1.stop_at_bound, args=[0]).start()
        l1 = LoopSimple(c1)
        l1.play_buffer()
        c1.get_stop_event().clear()
        Timer(5, c1.stop_at_bound, args=[0]).start()
        l1.play_buffer()


    test2()
