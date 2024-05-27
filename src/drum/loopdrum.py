from random import random, choices
from threading import Timer

import numpy as np

from buffer.loopsimple import LoopSimple
from buffer.wrapbuffer import WrapBuffer
from drum.basedrum import BaseDrum
from song.songpart import SongPart
from utils.utilaudio import AUDIO


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts. """

    _LOOP_PLAY_WGHT: list[int] = [7, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]

    def __init__(self):
        BaseDrum.__init__(self)
        self.__play_lst: list[LoopSimple] = list()  # list to play sounds, changed by randomizes
        self.songpart: SongPart | None = None
        self._par = 0.2  # for this drum - probability to randomize at bar start

    def start(self) -> None:
        if not self.songpart:
            return
        self._is_stopped = False

    def is_playable(self, buff: WrapBuffer) -> bool:
        return id(self.songpart) != id(buff)

    def randomize(self) -> None:
        if not self.songpart:
            return
        self.__play_lst.clear()
        self.songpart.loops.apply_to_each(lambda x: self.__play_lst.append(x))
        max_len = self.songpart.loops.item_count()
        play_len = min(3, max_len)
        self.__play_lst = choices(self.__play_lst, weights=self._LOOP_PLAY_WGHT[:max_len], k=play_len)

    def play_fill(self, idx: int) -> None:
        if not self.songpart:
            return
        self.__play_lst.clear()
        self.songpart.loops.apply_to_each(lambda x: self.__play_lst.append(x))
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / AUDIO.SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.randomize()
        for loop in self.__play_lst:
            loop.play_samples(out_data, idx)

    def iterate_config(self, steps: int) -> None:
        pass

    def show_config(self) -> str:
        return ""

    def show_param(self) -> str:
        return super().show_param()

    def get_config(self) -> str:
        return ""

    def set_config(self, config: str = None) -> None:
        pass
