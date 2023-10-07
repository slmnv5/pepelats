from __future__ import annotations

import random
from configparser import ConfigParser

from buffer.loopsimple import LoopSimple
from drum._sampleloader import SampleLoader
from drum.loopdrum import LoopDrum
from song.songpart import SongPart
from utils.utilconfig import find_path
from utils.utillog import get_my_log
from utils.utilother import FileFinder, EuclidSlicer

my_log = get_my_log(__name__)


class EuclidDrum(LoopDrum):

    def __init__(self):
        LoopDrum.__init__(self, SongPart(0))
        self._ptn_dic: dict[str, dict[str, str]] = dict()
        self._dname = find_path("config/drum/euclid")
        self._ff = FileFinder(self._dname, True, ".ini")
        assert self._ff.selected_item()

    def get_config(self) -> str:
        return self._ff.selected_item()

    def show_drum_config(self) -> str:
        return self._ff.get_str()

    def iterate_drum_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def get_id(self) -> int:
        return id(self)

    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        self.stop_drum()
        if config:
            k = self._ff.find_item_idx(config)
            self._ff.select_idx(k)
        bar_len = self._bar_len if bar_len is None else bar_len
        if not bar_len:
            return
        cfg = ConfigParser()
        cfg.read(self._ff.get_full_name())
        self._ptn_dic = {s: dict(cfg.items(s)) for s in cfg.sections() if s in SampleLoader.get_sound_names()}
        self._set_bar_len(bar_len)
        self.start_drum()

    def _get_option(self, option: str, default: str) -> int:
        val_str = self._ptn_dic.get(option, default)
        val_lst = val_str.split(",")
        val_str = random.choice(val_lst)
        return int(val_str)

    def _set_bar_len(self, bar_len: int) -> None:
        super()._set_bar_len(bar_len)
        if not bar_len:
            return

        self._part = SongPart(bar_len)
        while self._part.loops.item_count() < len(self._ptn_dic):
            self._part.loops.add_item(LoopSimple(bar_len))
        base_steps = 16
        loops = self._part.loops
        for k, sound in enumerate(self._ptn_dic.keys()):
            steps: int = self._get_option("steps", "16")
            beats: int = self._get_option("beats", "4")
            offset: int = self._get_option("offset", "0")
            accent: int = self._get_option("accent", "2")
            es = EuclidSlicer(steps, beats, offset)

            if k == 0:
                base_steps = steps
                lp = loops.select_idx(0)
                step_len = bar_len / base_steps
            else:
                new_len = round(bar_len * steps / base_steps)
                step_len = new_len / steps
                lp = LoopSimple(new_len)
                loops.add_item(lp)

            for n, s in enumerate(es.get_ptrn_str()):
                if s == '.':
                    continue
                pos = round(n * step_len)
                is_accent = n % accent == 0
                sound_arr = SampleLoader.get_sound(sound, is_accent)
                lp.record_samples(sound_arr, pos)

    def random_drum(self) -> None:
        super().random_drum()

    def change_drum_level(self, chg: int) -> None:
        super().change_drum_level(chg)
