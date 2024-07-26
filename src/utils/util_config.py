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
SOCK_PORT: int = 10000
LOCAL_IP: str = ""
GATEWAY_IP: str = ""

if os.name == "posix":
    s = subprocess.run(["ip", "route"], stdout=subprocess.PIPE).stdout.decode()
    LOCAL_IP = split_to_dict(s, "\n", " src ", " metric ", " ", " ").get("dhcp", "")
    GATEWAY_IP = split_to_dict(s, "\n", " via ", " dev ", " ", " ").get("default", "")
elif os.name == "nt":
    s = subprocess.run(["ipconfig"], stdout=subprocess.PIPE).stdout.decode()
    LOCAL_IP = split_to_dict(s, "\n", "IPv4", ": ", " .", " \r\n\t").get("Address", "")
    GATEWAY_IP = split_to_dict(s, "\n", "Default", ": ", " .", " \r\n\t").get("Gateway", "")
else:
    pass

    assert all(x.isdigit() or x == "." for x in LOCAL_IP)
    assert all(x.isdigit() or x == "." for x in GATEWAY_IP)

MY_LOG.info(f"Gateway IP is: {GATEWAY_IP}, Local IP is: {LOCAL_IP}")


def load_ini_section(sect: str, convert: bool = False) -> dict[str, str]:
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


if __name__ == "__main__":
    print("IPs:", LOCAL_IP, GATEWAY_IP)
