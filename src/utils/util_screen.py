from basic.audioinfo import AudioInfo

_UPDATES_PER_LOOP: int = 16


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
    tmp["sleep_tm"] = 1.0
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
