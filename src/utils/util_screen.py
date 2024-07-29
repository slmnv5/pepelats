import os

from basic.audioinfo import AudioInfo
from utils.util_config import load_ini_section
from utils.util_log import MY_LOG
from utils.util_name import AppName

SCREEN_TYPE: int = load_ini_section("SCREEN", True).get(AppName.screen_type, 0)

try:
    SCR_COLS, SCR_ROWS = os.get_terminal_size()
except OSError:
    SCR_COLS, SCR_ROWS = 30, 10  # if running inside python IDE

MY_LOG.info(f"Text screen size: cols={SCR_COLS} rows={SCR_ROWS}")

_UPDATES_PER_LOOP: int = 16


def recalc_dic(dic: dict) -> None:
    dic["sleep_tm"] = dic["len"] / AudioInfo().SD_RATE / _UPDATES_PER_LOOP
    dic["pos"] = (dic["idx"] % dic["len"]) / dic["len"]
    dic["delta"] = 1 / _UPDATES_PER_LOOP
    if dic["max_loop_len"] > dic["len"]:
        dic["max_loop_pos"] = (dic["idx"] % dic["max_loop_len"]) / dic["max_loop_len"]
        dic["max_loop_delta"] = 1 / _UPDATES_PER_LOOP / dic["max_loop_len"] * dic["len"]
    else:
        dic["max_loop_pos"], dic["max_loop_delta"] = 0, 0


def get_default_dict() -> dict[str, str | float]:
    tmp: dict = dict()
    tmp[AppName.header] = ""
    tmp[AppName.description] = ""
    tmp[AppName.content] = ""
    tmp["idx"] = 0
    tmp["is_rec"] = False
    tmp["len"] = 100_000
    tmp["max_loop_len"] = 100_000
    return tmp
