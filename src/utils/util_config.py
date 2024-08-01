import os
import subprocess
from configparser import ConfigParser

from utils.util_log import MY_LOG
from utils.util_name import AppName
from utils.util_other import split_to_dict

s: str = subprocess.run(["git", "branch"], stdout=subprocess.PIPE).stdout.decode()
s = s[s.find("* ") + 2:]
BRANCH = s[:s.find("\n")].strip()

LOCAL_PORT: int = 8000
CONFIG_PORT: int = 9000
LOCAL_IP: str = ""

if os.name == "posix":
    s = subprocess.run(["ip", "route"], stdout=subprocess.PIPE).stdout.decode()
    LOCAL_IP = split_to_dict(s, "metric ", "dhcp ", " ", " ", " ").get("src", "")
elif os.name == "nt":
    s = subprocess.run(["ipconfig"], stdout=subprocess.PIPE).stdout.decode()
    LOCAL_IP = split_to_dict(s, "\n", "IPv4", ": ", " .", " \r\n\t").get("Address", "")
else:
    pass

assert len(LOCAL_IP) >= 7 and all(x.isdigit() or x == "." for x in LOCAL_IP)
MY_LOG.info(f"Local IP is: {LOCAL_IP}")


def ram_usage_pct() -> int:
    if os.name != "posix":
        return 0
    try:
        line = subprocess.run(["free", "-m"], stdout=subprocess.PIPE).stdout.decode()
        line = line.split('\n')[1]
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


def get_params(path: str) -> dict[str, str | int | float]:
    if "?" not in path:
        return dict()
    k = path.index("?") + 1
    lst: list[list[str]] = [x.split("=") for x in path[k:].split("&")]
    lst: list[tuple[str, str]] = [(x[0], x[1]) for x in lst if len(x) == 2]
    return dict([(k, convert_param(v)) for (k, v) in lst])


if __name__ == "__main__":
    pass
