import numpy as np

from drum._ptrnloader import PtrnLoader
from utils.util_audio import make_buffer
from utils.util_config import load_ini_section
from utils.util_name import AppName
from utils.util_numpy import from_data_to_buff
from utils.util_other import EuclidSlicer, FileFinder


class EuclidPtrnLoader(PtrnLoader):
    _BAR_STEPS: int = 16  # each bar has so many steps

    def __init__(self):
        PtrnLoader.__init__(self)
        self.break_marker = load_ini_section("DRUM").get(AppName.euclid_break, "")
        dname = f"{AppName.drum_config_dir}/euclid"
        self.ff = FileFinder(dname, True, ".ini")
        if not self.ff.get_item():
            raise RuntimeError(f"No INI files in: {dname}")

    def fn_load(self, ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        for sname, euclid_str in sect_dic.items():
            ptn_lst = [int(x) for x in euclid_str.split(",")]
            if ptn_lst[0] and ptn_lst[1]:
                ptn_dic[sname] = EuclidSlicer(ptn_lst[0], ptn_lst[1], ptn_lst[2], ptn_lst[3]).get_ptrn_str()
        # MY_LOG.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    def fn_convert(self, bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        result = list()
        for sname, notes in ptn_dic.items():
            new_len = round(bar_len * len(notes) / EuclidPtrnLoader._BAR_STEPS)
            buff = make_buffer(new_len)
            result.append(buff)
            step_len: float = new_len / len(notes)
            for k, s in enumerate(notes):
                if s not in "+*":
                    continue
                idx = round(k * step_len)
                if k % 2 != 0:
                    chg = round(step_len * par * 0.25)
                    idx += chg
                sound_arr = self.sample_loader.get_sound(sname, s == "*")
                from_data_to_buff(buff, sound_arr, idx)

        return result

    def fn_intensity(self, ptn_dic: dict[str, str]) -> float:
        """ Calculate pattern intensity """
        result: float = 0.0
        for sname, notes in ptn_dic.items():
            for s in notes:
                if s not in "+*":
                    continue
                is_accent = s == '*'
                result += self.sample_loader.get_energy(sname, is_accent) / len(notes)
        return round(result, 2)
