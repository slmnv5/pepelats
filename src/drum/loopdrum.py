import random

import numpy as np

from drum.basedrum import BaseDrum
from song.songpart import SongPart


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base """

    def __init__(self, part: SongPart):
        BaseDrum.__init__(self)
        self._part: SongPart = part

    def get_config(self) -> str:
        return ""

    def _get_drum_levels(self) -> int:
        cnt = self._part.loops.item_count()
        if cnt < 3:
            return 1
        elif cnt < 5:
            return 2
        else:
            return 3

    def get_id(self) -> int:
        return id(self._part)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._part.is_silent or self._part.is_empty:
            return
        self._part.play_samples(out_data, idx)

    def random_drum(self) -> None:
        loops = self._part.loops
        lp_max = loops.item_count()
        assert lp_max > 0
        lp_fraction: float = (self._drum_level + 1) / self._get_drum_levels()
        assert 0 < lp_fraction <= 1
        lp_cnt: int = round(lp_max * lp_fraction)
        lp_lst = list(range(1, lp_max))
        for _ in range(lp_cnt - 1):
            k = random.choice(lp_lst)
            lp_lst.remove(k)
            loops.select_idx(k).set_silent(False)
        for k in lp_lst:
            loops.select_idx(k).set_silent(True)
        self.start_drum()

    # noinspection PyMethodMayBeStatic
    def get_volume(self) -> float:
        return 1.0

    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        self.stop_drum()
        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)
        self.start_drum()

    def iterate_drum_config(self, steps: int) -> None:
        self._part.loops.iterate(steps)

    def show_drum_config(self) -> str:
        return self._part.loops.get_str()

    def stop_drum(self) -> None:
        self._part.set_silent(True)

    def start_drum(self) -> None:
        self._part.set_silent(False)

    def __str__(self) -> str:
        lp_lst: list[str] = list()
        loops = self._part.loops
        for k in range(loops.item_count()):
            silent = loops.select_idx(k).is_silent
            lp_lst.append("S" if silent else "_")
        return "L:" + "".join(lp_lst)

    def show_drum_param(self) -> str:
        return f"{self}:{self._part}"
