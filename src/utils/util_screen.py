import os
import sys

from utils.util_audio import AUDIO_INFO
from utils.util_config import load_ini_section
from utils.util_log import MY_LOG
from utils.util_name import AppName

SCREEN_TYPE: int = load_ini_section("SCREEN", True).get(AppName.screen_type, 0)

try:
    SCR_COLS, SCR_ROWS = os.get_terminal_size()
except OSError:
    SCR_COLS, SCR_ROWS = 30, 10  # if running inside python IDE

MY_LOG.info(f"Text screen size: cols={SCR_COLS} rows={SCR_ROWS}")

_UPDATES_PER_LOOP: float = 16

if AppName.no_progress in sys.argv:
    _UPDATES_PER_LOOP: float = 0.001


def recalc_dic(dic: dict) -> None:
    dic["sleep_tm"] = dic["len"] / AUDIO_INFO.SD_RATE / _UPDATES_PER_LOOP
    dic["pos"] = (dic["idx"] % dic["len"]) / dic["len"]
    dic["delta"] = 1 / _UPDATES_PER_LOOP
    if dic["max_loop_len"] > dic["len"]:
        dic["max_loop_pos"] = (dic["idx"] % dic["max_loop_len"]) / dic["max_loop_len"]
        dic["max_loop_delta"] = 1 / _UPDATES_PER_LOOP / dic["max_loop_len"] * dic["len"]
    else:
        dic["max_loop_pos"], dic["max_loop_delta"] = 0, 0


DEFAULT_DIC = {
    AppName.header: "", AppName.description: "", AppName.content: "",
    "idx": 0, "is_rec": False, "len": 100_000,
    "max_loop_len": 100_000
}
