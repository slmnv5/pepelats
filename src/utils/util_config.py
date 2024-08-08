import os
import subprocess
from configparser import ConfigParser

from utils.util_log import MY_LOG
from utils.util_name import AppName
from utils.util_other import split_to_dict


def _get_branch_lst() -> list[str]:
    br_str: str = subprocess.run(["git", "branch"], stdout=subprocess.PIPE).stdout.decode()
    return [x for x in br_str.splitlines()]


def get_branch_update():
    return subprocess.run(["git", "log", "-1", "--format=%ch"], stdout=subprocess.PIPE).stdout.decode()


def get_selected_branch() -> str:
    lst = [x for x in _get_branch_lst() if x.startswith("* ")]
    return lst[0] if lst else ""


LOCAL_PORT: int = 8000


def get_local_ip() -> str:
    if os.name == "posix":
        s = subprocess.run(["ip", "route"], stdout=subprocess.PIPE).stdout.decode()
        s = split_to_dict(s, "metric ", "dhcp ", " ", " ", " ").get("src", "")
    elif os.name == "nt":
        s = subprocess.run(["ipconfig"], stdout=subprocess.PIPE).stdout.decode()
        s = split_to_dict(s, "\n", "IPv4", ": ", " .", " \r\n\t").get("Address", "")
    else:
        s = "Implemented only on Windows and Linux"
    if not (7 <= len(s) <= 15 and s.replace(".", "").isdigit()):
        MY_LOG.error(f"Faled to get LOCAL_IP: {s}")
        return ""
    MY_LOG.info(f"LOCAL_IP: {s}")
    return s


LOCAL_IP: str = get_local_ip()


def ram_usage_pct() -> int:
    if os.name != "posix":
        return 0
    try:
        line = subprocess.run(["free", "-m"], stdout=subprocess.PIPE).stdout.decode()
        line = line.splitlines()[1]
        assert line.startswith("Mem:")
        lst = [convert_param(x) for x in line.split()[1:4]]
        assert len(lst) == 3
        assert all(isinstance(x, int) for x in lst)
        return round((1 - lst[2] / lst[0]) * 100)
    except Exception as ex:
        MY_LOG.warning(f"Failed calculate RAM usage: {ex}")
        return 0


def cpu_usage_pct() -> int:
    if os.name != "posix":
        return 0
    try:
        line = subprocess.run(["head", "-n", "1", '/proc/stat'], stdout=subprocess.PIPE).stdout.decode()
        assert line.startswith("cpu")
        lst = [convert_param(x) for x in line.split()[1:5]]
        assert len(lst) == 4
        assert all(isinstance(x, int) for x in lst)
        return round((1 - lst[3] / sum(lst)) * 100)
    except Exception as ex:
        MY_LOG.warning(f"Failed calculate CPU usage: {ex}")
        return 0


def load_ini_section(sect: str, convert: bool = False) -> dict[str, str | int | float]:
    main = AppName.main_ini
    local = AppName.local_ini
    assert os.path.isfile(main)
    cfg = ConfigParser()
    cfg.read([main, local])  # local file overwrites main

    if sect not in cfg.sections():
        return dict()
    elif not convert:
        return dict(cfg.items(sect))
    else:
        return {k: convert_param(v) for (k, v) in cfg.items(sect)}


def update_ini_section(sect: str, dic: dict[str, str]) -> None:
    local = AppName.local_ini
    cfg = ConfigParser()
    cfg.read(local)
    if sect not in cfg.sections():
        cfg.add_section(sect)
    for k, v in dic.items():
        cfg.set(sect, k, v)
    with open(local, "w") as f:
        cfg.write(f)


def convert_param(param: str) -> str | int | float:
    tmp = param.replace(" ", "")
    if tmp.strip("+-").isdigit():
        return int(tmp)
    elif tmp.strip("+-").replace(".", "", 1).isdigit():
        return float(tmp)
    else:
        return param


try:
    SCR_COLS, SCR_ROWS = os.get_terminal_size()
except OSError:
    SCR_COLS, SCR_ROWS = 30, 10  # if running inside python IDE

MY_LOG.info(f"Text screen size: cols={SCR_COLS} rows={SCR_ROWS}")

if __name__ == "__main__":
    pass
