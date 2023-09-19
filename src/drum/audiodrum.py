from __future__ import annotations

from math import ceil

from drum._sampleloader import SampleLoader
from drum.patterndrum import PatternDrum
from utils.utilconfig import find_path
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class AudioDrum(PatternDrum):

    def __init__(self):
        PatternDrum.__init__(self, find_path("config/drum/audio"))
        self._set_bar_len(0)

    def get_config(self) -> str:
        return self._ff.selected_item()

    @staticmethod
    def load_one_ptn(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, any]) -> None:
        """One Drum pattern put into dictionary"""
        sound_lst = SampleLoader.get_sound_names()
        max_steps: int = max([len(v) for k, v in sect_dic.items() if k in sound_lst])
        accents: str = sect_dic.get("ac", ".")
        accents = (accents * ceil(max_steps / len(accents)))[:max_steps]
        assert type(accents) == str and len(accents) == max_steps
        ptn_dic["accents"] = accents
        for sname, notes in [(k, v) for (k, v) in sect_dic.items() if k in sound_lst and v]:
            assert type(notes) == str and len(notes) > 0
            notes = (notes * ceil(max_steps / len(notes)))[:max_steps]
            ptn_dic[sname] = notes
        my_log.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    @staticmethod
    def convert_one_ptn(bar_len: int, ptn_dic: dict[str, any], ptn_list: list[tuple]) -> None:
        """One Drum pattern converted into play list of (buff_position, skip_prob, is_accent, sound_name)"""
        accents: str = ptn_dic["accents"]
        steps = len(accents)
        step_len = bar_len / steps
        sound_lst = SampleLoader.get_sound_names()
        for sound, notes in [(k, v) for k, v in ptn_dic.items() if k in sound_lst]:
            assert steps == len(notes)
            for k in range(steps):
                if notes[k] not in "123456789!":
                    continue
                step_prob = "0123456789!".index(notes[k]) / 10
                is_accent = accents[k] != "."
                idx = round(k * step_len)
                skip_prob = round(1 - step_prob, 2)
                ptn_list.append((idx, skip_prob, is_accent, sound))
        my_log.debug(f"Converted drum pattern:\n{ptn_list}")
