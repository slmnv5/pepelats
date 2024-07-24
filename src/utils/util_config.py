import os
import subprocess
from configparser import ConfigParser

from utils.util_name import AppName

s = subprocess.run(['git', 'branch'], stdout=subprocess.PIPE)
s = s.stdout.decode()
s = s[s.find("* ") + 2:]
BRANCH = s[:s.find("\n")].strip()

if os.name == 'posix':
    s = subprocess.run(['hostname', '-I'], stdout=subprocess.PIPE)
    IP_ADDR = s.stdout.decode()
elif os.name == 'nt':
    s = subprocess.run(['ipconfig'], stdout=subprocess.PIPE)
    s = s.stdout.decode()
    IP_ADDR = s[s.rfind(": ") + 2:].strip()
    assert all(x.isdigit() or x == '.' for x in IP_ADDR)
else:
    raise RuntimeError("OS must be posix or nt")


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
    with open(local, 'w') as f:
        cfg.write(f)


def convert_param(param: str) -> str | int | float:
    tmp = param.replace(' ', '')
    if tmp.strip('+-').isdigit():
        return int(tmp)
    elif tmp.strip('+-').replace('.', '', 1).isdigit():
        return float(tmp)
    else:
        return param
