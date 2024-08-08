import sys

from utils.util_audio import AUDIO_INFO
from utils.util_name import AppName


class BaseScreen:
    _NO_PROGRESS: bool = AppName.dash_no_progress in sys.argv
    _UPDATES_PER_LOOP: float = 0.01 if _NO_PROGRESS else 16.0
    _DEFAULT_DIC = {
        AppName.header: "", AppName.description: "", AppName.content: "",
        "idx": 0, "is_rec": False, "len": 1_000_000, "max_loop_len": 1_000_000
    }

    def __init__(self):
        self.__dic: dict[str, str | int | float] = self._DEFAULT_DIC
        self._recalc_dic(self.__dic)

    def _get_dic(self) -> dict[str, str | int | float]:
        return self.__dic

    def _recalc_dic(self, dic: dict[str, str | int | float]) -> dict[str, str | int | float]:
        dic["sleep_tm"] = dic["len"] / AUDIO_INFO.SD_RATE / self._UPDATES_PER_LOOP
        dic["pos"] = (dic["idx"] % dic["len"]) / dic["len"]
        dic["delta"] = 1 / self._UPDATES_PER_LOOP
        if dic["max_loop_len"] > dic["len"]:
            dic["max_loop_pos"] = (dic["idx"] % dic["max_loop_len"]) / dic["max_loop_len"]
            dic["max_loop_delta"] = 1 / self._UPDATES_PER_LOOP / dic["max_loop_len"] * dic["len"]
        else:
            dic["max_loop_pos"], dic["max_loop_delta"] = 0, 0

        self.__dic |= dic
        return self.__dic
