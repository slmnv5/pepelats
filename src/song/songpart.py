import numpy as np

from control.loopctrl import LoopCtrl
from song.loopsimple import LoopSimple
from utils.utilconfig import MAX_LEN
from utils.utilother import CollectionOwner


class SongPart(LoopSimple):
    """SongPart includes many simple loops to play together"""

    def __init__(self, sz: int = MAX_LEN):
        LoopSimple.__init__(self, sz)
        self.loops: CollectionOwner[LoopSimple] = CollectionOwner[LoopSimple](self)
        self.__undo: list[LoopSimple] = list()

    def get_max_len(self) -> int:
        loops = self.loops
        len_lst: list[int] = list()
        loops.apply_to_each(lambda x: len_lst.append(x.get_len()))
        return max(len_lst)

    def correct_buffer(self) -> None:
        for loop in self.__undo:
            loop.correct_buffer()
        self.loops.apply_to_each(lambda x: LoopSimple.correct_buffer(x))

    def trim_buffer(self, ctrl: LoopCtrl) -> None:
        loop: LoopSimple = self.loops.get_item()
        if not loop.is_empty:
            return
        drum = ctrl.get_drum()
        bar_len = drum.get_bar_len()
        part_len = self.get_len()
        base_len = bar_len if self.is_empty else max(bar_len, part_len)
        loop.finalize(ctrl.idx, base_len)
        if not bar_len:
            ctrl.drum_create(ctrl.idx)

    def play(self, out_data: np.ndarray, idx: int) -> None:
        self.loops.apply_to_each(lambda x: LoopSimple.play(x, out_data, idx))

    def record(self, in_data: np.ndarray, idx: int) -> None:
        loop = self.loops.get_item()
        LoopSimple.record(loop, in_data, idx)

    def redo(self) -> bool:
        if not self.__undo:
            return False
        item = self.__undo.pop()
        self.loops.idx_from_item(item)
        return True

    def undo(self) -> bool:
        self.loops.select_idx(-1)
        item = self.loops.delete_selected()
        if not item:
            return False
        self.__undo.append(item)
        return True

    def clear_undo(self) -> None:
        self.__undo.clear()

    def __str__(self):
        if self.is_empty:
            return "---------------"
        return f"{LoopSimple.__str__(self)}  {self.loops.item_count():02}/{len(self.__undo):02}"
