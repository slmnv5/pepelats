import os
import sys
from configparser import ConfigParser

from utils.utillog import MyLog

APPDIR = os.sep + 'pepelats'

my_log = MyLog()


class ConfigName:
    # menu and midi config related
    default_config: str = "default_config"
    update_method: str = "update_method"
    description: str = "description"
    comment: str = "comment"
    client_redraw: str = "_redraw"  # this is MenuClient command to update screen
    play_section: str = "play"
    menu_dir: str = "menu_dir"
    main_ini: str = "main.ini"
    midi_out: str = "midi_out"
    midi_in: str = "midi_in"


def find_path(path_end: str) -> str:
    """Find file or dir. creates one if missing"""
    tmp1 = os.getcwd() + os.sep + path_end
    pos = tmp1.find(APPDIR)
    if pos >= 0:
        return tmp1[:pos + len(APPDIR)] + os.sep + path_end
    else:
        my_log.error(f"Path not found: {path_end}")
        return path_end


def load_ini_section(fname: str, sect: str) -> dict[str, str]:
    assert os.path.isfile(fname) and sect
    cfg = ConfigParser()
    cfg.read(fname)
    sect = next((x for x in cfg.sections() if x == sect), "DEFAULT")
    return dict(cfg.items(sect))


def update_ini_section(fname: str, sect: str, dic: dict[str, str]) -> None:
    assert os.path.isfile(fname) and sect
    cfg = ConfigParser()
    cfg.read(fname)
    for k, v in dic.items():
        cfg.set(sect, k, v)
    with open(fname, 'w') as f:
        cfg.write(f)


KEEP_SCREEN = "--keep_screen" in sys.argv
