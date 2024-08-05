import numpy as np

from drum.basedrum import BaseDrum
from song.loopsimple import LoopSimple
from utils.util_audio import AUDIO_INFO
from utils.util_other import CollectionOwner


class SongPart(LoopSimple):
    """SongPart includes many simple loops to play together"""

    def __init__(self):
        LoopSimple.__init__(self)
        self.loops = CollectionOwner[LoopSimple]()
        self.__undo: list[LoopSimple] = list()
        self.__init_len: int = 0  # first recorded loop length
        self.__info_str: str = "-" * 15  # info for first recoded loop

    def is_empty(self) -> bool:
        return self.__init_len == 0

    def get_base_len(self, drum: BaseDrum) -> int:
        """ max len of drum and all loops """
        lst: list[int] = [super().get_base_len(drum)]
        self.loops.for_each(lambda x: lst.append(x.get_len()))
        return max(lst)

    def rec_on(self) -> None:
        super().rec_on()
        self._state.start_idx = self._state.idx

    def trim_buffer(self, idx: int, base_len: int) -> None:
        self._trim(idx, base_len, self._state.start_idx)
        self._state.start_idx = 0
        self.append_itself()

    def append_itself(self) -> None:
        if self.loops.item_count() == 0:
            self.__init_len = self.get_len()
            self.__info_str = self.get_decibel() + self.get_seconds()
        loop = LoopSimple(buff=self.get_buff())
        self.set_buff(AUDIO_INFO.get_zero_buffer(self.__init_len))
        self.loops.add_item(loop)
        self.clear_undo()

    def correct_buffer(self) -> None:
        self.loops.for_each(lambda x: x.correct_buffer())
        for z in self.__undo:
            z.correct_buffer()

    def clear(self) -> None:
        self.max_buffer()
        self.__undo.clear()
        self.loops = CollectionOwner[LoopSimple]()
        self.__info_str = "-" * 15
        self.__init_len = 0

    def play(self, out_data: np.ndarray, idx: int) -> None:
        # LoopSimple.play(self, out_data, idx)
        self.loops.for_each(lambda x: x.play(out_data, idx))

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
        return f"{self.__info_str} {self.loops.item_count():02}/{len(self.__undo):02}"
