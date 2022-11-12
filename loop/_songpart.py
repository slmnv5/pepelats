from threading import Timer

import numpy as np

from drum import RDRUM
import logging
from loop._loopsimple import LoopWithDrum
from loop._oneloopctrl import OneLoopCtrl
from loop._player import Player
from loop._wrapbuffer import WrapBuffer
from utils import CollectionOwner


class SongPart(CollectionOwner[LoopWithDrum], Player):
    """Loop that includes many more simple loops to play together"""

    def __init__(self, ctrl: OneLoopCtrl):
        Player.__init__(self, ctrl)
        CollectionOwner.__init__(self, LoopWithDrum(ctrl))

    def set_ctrl(self, ctrl) -> None:
        Player.set_ctrl(self, ctrl)
        self.apply_to_each(lambda x: x.set_ctrl(ctrl), use_undo=True)

    def trim_buffer(self, idx: int) -> None:
        """create drums of correct length if drum is empty,
        otherwise trims self.length to multiple of first loop in the part"""
        logging.debug(f"trim_buffer {self.__class__.__name__} idx {idx}")
        self.get_item().trim_buffer(idx)

    @property
    def is_empty(self) -> bool:
        return self.get_first().is_empty

    @property
    def length(self) -> int:
        return self.get_first().length

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        RDRUM.play_samples(out_data, idx)
        self.apply_to_each(lambda x: WrapBuffer.play_samples(x, out_data, idx))

    def record_samples(self, in_data: np.ndarray, idx: int) -> None:
        loop = self.get_item()
        WrapBuffer.record_samples(loop, in_data, idx)

    def __str__(self):
        if not RDRUM.get_length() or self.is_empty:
            return "---------"
        if not self._collection_str:
            first = self.get_first()
            self._collection_str = f"L:{first.length // RDRUM.get_length():02} " \
                                   f"V:{first.volume:02} {self.item_count:02}/{self.undo_count:02}"
        return self._collection_str


if __name__ == "__main__":
    def test2():
        c1 = OneLoopCtrl()
        c1._is_rec = True
        Timer(3, c1.stop_at_bound, args=[0]).start()
        l1 = SongPart(c1)
        l1.play_buffer()
        c1.get_stop_event().clear()
        Timer(5, c1.stop_at_bound, args=[0]).start()
        l1.play_buffer()
        l1.set_ctrl(c1)


    test2()
