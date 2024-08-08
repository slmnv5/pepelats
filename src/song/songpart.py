import numpy as np

from drum.basedrum import BaseDrum
from song.loopsimple import LoopSimple
from song.wrapbuffer import WrapBuffer
from utils.util_other import CollectionOwner


class SongPart(LoopSimple):
    """SongPart includes many simple loops to play together"""

    def __init__(self):
        LoopSimple.__init__(self)
        self.loops = CollectionOwner[LoopSimple](self)
        self.__undo: list[LoopSimple] = list()

    def _record(self, in_data: np.ndarray, idx: int) -> None:
        loop = self.loops.get_item()
        LoopSimple._record(loop, in_data, idx)

    def get_base_len(self, drum: BaseDrum) -> int:
        """ max len of drum and all loops """
        lst: list[int] = [drum.get_bar_len()]
        self.loops.for_each(lambda x: lst.append(x.get_len()) if not x.is_empty() else None)
        return max(lst)

    def rec_on(self) -> None:
        super().rec_on()
        self._state.start_idx = self._state.idx

    def trim_buffer(self, idx: int, base_len: int) -> None:
        loop = self.loops.get_item()
        loop._trim(idx, base_len, self._state.start_idx)
        self._state.start_idx = 0

    def correct_buffer(self) -> None:
        self.loops.for_each(lambda x: LoopSimple.correct_buffer(x))
        for z in self.__undo:
            z.correct_buffer()

    def clear(self) -> None:
        self.max_buffer()
        self.__undo.clear()
        self.loops = CollectionOwner[LoopSimple](self)

    def play(self, out_data: np.ndarray, idx: int) -> None:
        self.loops.for_each(lambda x: WrapBuffer.play(x, out_data, idx))

    def redo(self) -> bool:
        if not self.__undo:
            return False
        item = self.__undo.pop()
        self.loops.add_item(item)
        return True

    def undo(self) -> bool:
        self.loops.select_idx(-1)
        item = self.loops.delete_item()
        if not item:
            return False
        self.__undo.append(item)
        return True

    def clear_undo(self) -> None:
        self.__undo.clear()

    def __str__(self):
        if self.is_empty():
            return "-" * 15
        if not self._info_str:
            self._info_str = f"{self.get_decibel()} {self.get_seconds()}"

        return f"{self._info_str} {self.loops.item_count():02}/{len(self.__undo):02}"
