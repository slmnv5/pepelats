import numpy as np

from control.loopctrl import LoopCtrl
from song.loopsimple import LoopSimple
from utils.utilother import CollectionOwner


class SongPart(LoopSimple, CollectionOwner[LoopSimple]):
    """SongPart includes many simple loops to play together"""

    def __init__(self):
        LoopSimple.__init__(self)
        CollectionOwner.__init__(self, self)
        self.__undo: list[LoopSimple] = list()

    def get_max_len(self) -> int:
        max_len = 0
        for x in self.get_list():
            max_len = max(LoopSimple.get_len(x), max_len)
        return max_len

    def correct_buffer(self) -> None:
        for x in self.__undo:
            x.correct_buffer()
        for x in self.get_list():
            LoopSimple.correct_buffer(x)

    def trim_buffer(self, ctrl: LoopCtrl) -> None:
        loop = self.get_item()
        if not loop.is_empty:
            return
        drum = ctrl.get_drum()
        bar_len = drum.get_bar_len()
        max_part_len = self.get_max_len()
        base_len = bar_len if self.is_empty else max(bar_len, max_part_len)
        loop.finalize(ctrl.idx, base_len)
        if not bar_len:
            ctrl.drum_create(ctrl.idx)

    def play(self, out_data: np.ndarray, idx: int) -> None:
        for x in self.get_list():
            LoopSimple.play(x, out_data, idx)

    def record(self, in_data: np.ndarray, idx: int) -> None:
        loop = self.get_item()
        LoopSimple.record(loop, in_data, idx)

    def redo(self) -> bool:
        if not self.__undo:
            return False
        item = self.__undo.pop()
        self.add_item(item)
        return True

    def undo(self) -> bool:
        self.select_idx(-1)
        item = self.delete_selected()
        if not item:
            return False
        self.__undo.append(item)
        return True

    def clear_undo(self) -> None:
        self.__undo.clear()

    def __str__(self):
        if self.is_empty:
            return "---------------"
        return f"{LoopSimple.__str__(self)}  {self.item_count():02}/{len(self.__undo):02}"
