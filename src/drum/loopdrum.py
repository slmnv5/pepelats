import numpy as np

from drum.basedrum import BaseDrum
from song.songpart import SongPart


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The part will record real drum sounds and play along with all other parts """

    def __init__(self, part: SongPart):
        BaseDrum.__init__(self)
        self._part: SongPart = part

    def get_config(self) -> str:
        return ""

    def _get_drum_levels(self) -> int:
        cnt = self._part.loops.item_count()
        if cnt < 3:
            return 1
        else:
            return 2

    def get_id(self) -> int:
        return id(self._part)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._part.is_empty:
            return
        self._part.play_samples(out_data, idx)

    def change_drum_level(self, chg: int) -> None:
        super().change_drum_level(chg)

    def random_drum(self) -> None:
        loops = self._part.loops
        total_cnt = self._part.loops.item_count()
        play_cnt: int = 1 + self._drum_level * total_cnt // self._get_drum_levels()
        assert 0 < play_cnt <= total_cnt
        total_lst = list(range(total_cnt))
        play_lst = np.random.choice(total_lst, size=play_cnt, replace=False)
        for k in total_lst:
            lp = loops.select_idx(k)
            lp.set_silent(False if k in play_lst else True)

    # noinspection PyMethodMayBeStatic
    def get_volume(self) -> float:
        return 1.0

    # noinspection PyMethodMayBeStatic
    def get_par(self) -> float:
        return 1.0

    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        self.stop_drum()
        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)
        self.start_drum()

    def iterate_drum_config(self, steps: int) -> None:
        pass

    def show_drum_config(self) -> str:
        return ""

    def stop_drum(self) -> None:
        loops = self._part.loops
        loops.apply_to_each(lambda x: x.set_silent(True))

    def start_drum(self) -> None:
        self.random_drum()

    def __str__(self) -> str:
        lp_lst: list[str] = list()
        loops = self._part.loops
        loops.apply_to_each(lambda x: lp_lst.append("S" if x.is_silent else "_"))
        return "L:" + "".join(lp_lst)

    def show_drum(self) -> str:
        return f"{self}:{self._part}"

    def set_volume(self, volume: float) -> None:
        pass

    def set_par(self, par: float) -> None:
        pass
