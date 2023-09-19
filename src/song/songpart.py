from threading import Thread

import numpy as np

from buffer.loopctrl import LoopCtrl
from buffer.loopsimple import LoopSimple
from utils.utilconfig import MAX_LEN
from utils.utilother import CollectionOwner


class SongPart(LoopSimple):
    """SongPart includes many simple loops to play together"""

    def __init__(self, length: int = MAX_LEN):
        LoopSimple.__init__(self, length)
        self.loops = CollectionOwner[LoopSimple](self)
        self.undos = CollectionOwner[LoopSimple](LoopSimple(0))

    def trim_buffer(self, ctrl: LoopCtrl) -> None:
        loop: LoopSimple = self.loops.selected_item()
        if not loop.is_empty:
            return
        drum = ctrl.get_drum()
        bar_len = drum.get_bar_len()
        part_len = self.length
        base_len = bar_len if self.is_empty else max(bar_len, part_len)
        Thread(target=loop.finalize, args=(ctrl.idx, base_len, ctrl.start_rec)).start()
        if not bar_len:
            ctrl.add_command(["_load_drum_config", ctrl.idx])

    def play_samples(self, out_data: np.ndarray, idx: int, zero_buff: bool = False) -> None:
        self.loops.apply_to_each(lambda x: LoopSimple.play_samples(x, out_data, idx))

    def _record_samples(self, in_data: np.ndarray, idx: int) -> None:
        loop = self.loops.selected_item()
        LoopSimple._record_samples(loop, in_data, idx)

    def redo(self) -> bool:
        self.undos.select_idx(-1)
        item = self.undos.delete_selected()
        if not item:
            return False
        self.loops.add_item(item)
        return True

    def undo(self) -> bool:
        self.loops.select_idx(-1)
        item = self.loops.delete_selected()
        if not item:
            return False
        self.undos.add_item(item)
        return True

    def to_str(self) -> str:
        return f"{self.loops.item_count():02}/{self.undos.item_count() - 1:02}-{self}"
