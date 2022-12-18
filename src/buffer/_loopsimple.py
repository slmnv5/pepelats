from threading import Timer

import numpy as np

from buffer._oneloopctrl import OneLoopCtrl
from buffer._player import Player
from utils.config import MAX_LEN
from utils.log import LOGGER


class LoopSimple(Player):
    """Loop truncate itself to be multiple of drum if drum is ready.
    Or init drum of correct length if drum is empty"""

    def __init__(self, ctrl: OneLoopCtrl, length: int = MAX_LEN):
        super().__init__(ctrl, length)

    def _play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self.get_drum().play_drums(out_data, idx)
        super()._play_samples(out_data, idx)

    def trim_buffer(self) -> None:
        """create drums of correct length if drum is empty,
        otherwise trims self.length to multiple of drum length"""
        idx: int = self._ctrl.idx
        LOGGER.debug(f"trim_buffer {self.__class__.__name__} idx {idx}")
        drum = self.get_drum()
        if not drum.get_length():
            Timer(0.2, drum.prepare_drum, [idx]).start()
            self.finalize(idx, 0)
        else:
            self.finalize(idx, drum.get_length())

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
            self._str = f"L:{self.length // self.get_drum().get_length():02} V:{self.volume:.2F} " \
                        f"{self._show_properties()}"
        return self._str


if __name__ == "__main__":
    def test1():
        c1 = OneLoopCtrl()
        c1.set_is_rec(True)
        Timer(2, c1.stop_at_bound, args=[0]).start()
        l1 = LoopSimple(c1)
        l1.play_buffer()
        c1.get_stop_event().clear()
        Timer(3, c1.stop_at_bound, args=[0]).start()
        l1.play_buffer()
        print(f"Volume: {l1}")


    test1()
