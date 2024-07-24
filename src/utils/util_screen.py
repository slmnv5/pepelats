import os

from basic.audioinfo import AudioInfo
from utils.util_config import load_ini_section
from utils.util_log import MY_LOG
from utils.util_name import AppName

_UPDATES_PER_LOOP: int = 16

SCREEN_TYPE: int = load_ini_section("SCREEN", True).get(AppName.screen_type, 0)

try:
    SCR_COLS, SCR_ROWS = os.get_terminal_size()
except OSError:
    SCR_COLS, SCR_ROWS = 30, 10  # if running inside python IDE

MY_LOG.info(f"Text screen size: cols={SCR_COLS} rows={SCR_ROWS}")


def get_default_dict() -> dict:
    tmp: dict = dict()
    tmp["update_method"] = ""
    tmp["header"] = ""
    tmp["description"] = ""
    tmp["content"] = ""
    tmp["idx"] = 0
    tmp["is_rec"] = False
    tmp["len"] = 100_000
    tmp["max_loop_len"] = 100_000
    return tmp


def get_screen_dict(dic: dict) -> dict[str, any]:
    tmp: dict[str, any] = dict(dic)
    tmp["sleep_tm"] = dic["len"] / AudioInfo().SD_RATE / _UPDATES_PER_LOOP
    tmp["pos"] = (dic["idx"] % dic["len"]) / dic["len"]
    tmp["delta"] = 1 / _UPDATES_PER_LOOP
    if dic["max_loop_len"] > dic["len"]:
        tmp["max_loop_pos"] = (dic["idx"] % dic["max_loop_len"]) / dic["max_loop_len"]
        tmp["max_loop_delta"] = 1 / _UPDATES_PER_LOOP / dic["max_loop_len"] * dic["len"]
    else:
        tmp["max_loop_pos"], tmp["max_loop_delta"] = 0, 0
    return tmp
