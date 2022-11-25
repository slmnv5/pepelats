from threading import Timer

import numpy as np

from buffer import LoopSimple
from buffer import Player
from buffer import WrapBuffer
from drum import AudioDrum
from loopctrl import OneLoopCtrl
from utils.utilother import CollectionOwner


class SongPart(CollectionOwner[LoopSimple], Player):
    """Loop that includes many more simple loops to play together"""

    def __init__(self, ctrl: OneLoopCtrl):
        Player.__init__(self, ctrl)
        CollectionOwner.__init__(self, LoopSimple(ctrl))

    def set_ctrl(self, ctrl) -> None:
        Player.set_ctrl(self, ctrl)
        self.apply_to_each(lambda x: x.set_ctrl(ctrl), use_undo=True)

    def trim_buffer(self) -> None:
        """create drums of correct length if drum is empty,
        otherwise trims self.length to multiple of first loop in the part"""
        self.get_item().trim_buffer()

    @property
    def is_empty(self) -> bool:
        return self.get_id(0).is_empty

    @property
    def length(self) -> int:
        return self.get_id(0).length

    def _play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self.get_drum().play_drums(out_data, idx)
        self.apply_to_each(lambda x: WrapBuffer._play_samples(x, out_data, idx))

    def _record_samples(self, in_data: np.ndarray, idx: int) -> None:
        loop = self.get_item()
        loop._record_samples(in_data, idx)

    def __str__(self):
        if not self.get_drum().get_length() or self.is_empty:
            return "---------"
        if not self._collection_str:
            first = self.get_id(0)
            self._collection_str = f"L:{first.length // self.get_drum().get_length():02} " \
                                   f"V:{first.volume:02} {self.item_count:02}/{self.undo_count:02}"
        return self._collection_str


if __name__ == "__main__":
    def test2():
        c1 = OneLoopCtrl(AudioDrum())
        c1.__is_rec = True
        Timer(3, c1.stop_at_bound, args=[0]).start()
        l1 = SongPart(c1)
        l1.play_buffer()
        c1.get_stop_event().clear()
        Timer(5, c1.stop_at_bound, args=[0]).start()
        l1.play_buffer()
        l1.set_ctrl(c1)


    test2()
