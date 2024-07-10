import os
import sys
from configparser import ConfigParser

from utils.utillog import MyLog

APP_DIR = os.sep + 'pepelats'
SCR_COLS: int
SCR_ROWS: int
try:
    SCR_COLS, SCR_ROWS = os.get_terminal_size()
except OSError:
    SCR_COLS, SCR_ROWS = 30, 10

MyLog().info(f"Text screen size: cols={SCR_COLS} rows={SCR_ROWS}")


class ConfigName:
    # menu and midi config related
    update_method: str = "update_method"
    description: str = "description"
    menu_client_redraw: str = "_menu_client_redraw"
    menu_client_stop: str = "menu_client_stop"
    play_section: str = "play"
    menu_dir: str = "menu_dir"
    main_ini: str = "main.ini"
    local_ini: str = "local.ini"
    midi_out: str = "midi_out"
    midi_in: str = "midi_in"
    max_len_seconds: str = "max_len_seconds"
    device_name: str = "device_name"
    device_type: str = "device_type"
    sample_rate: str = "sample_rate"
    kbd_notes_linux: str = "kbd_notes_linux"
    kbd_notes_midi: str = "kbd_notes_midi"
    # drum config
    drum_type: str = "drum_type"
    drum_config: str = "drum_config"
    drum_volume: str = "drum_volume"
    drum_par: str = "drum_par"
    # drum types
    EuclidDrum: str = "EuclidDrum"
    StyleDrum: str = "StyleDrum"
    MidiDrum: str = "MidiDrum"
    LoopDrum: str = "LoopDrum"
    # saved dictionary with drum samples to avoid slow wav conversion
    pickled_drum_samples: str = "pickled_drum_samples.pkl"


def find_path(path_end: str) -> str:
    """ Find file or dir. """
    tmp1 = os.getcwd() + os.sep + path_end
    pos = tmp1.find(APP_DIR)
    if pos >= 0:
        return tmp1[:pos + len(APP_DIR)] + os.sep + path_end
    else:
        MyLog().error(f"Path not found: {path_end}")
        return path_end


def load_ini_section(sect: str) -> dict[str, str]:
    main = find_path(ConfigName.main_ini)
    local = find_path(ConfigName.local_ini)
    cfg = ConfigParser()
    cfg.read([main, local])  # local file overwrites main
    if sect not in cfg.sections():
        return dict()
    return dict(cfg.items(sect))


def update_ini_section(sect: str, dic: dict[str, str]) -> None:
    local = find_path(ConfigName.local_ini)
    cfg = ConfigParser()
    cfg.read(local)
    if sect not in cfg.sections():
        cfg.add_section(sect)
    for k, v in dic.items():
        cfg.set(sect, k, v)
    with open(local, 'w') as f:
        cfg.write(f)


KEEP_SCREEN: bool = "--keep_screen" in sys.argv
HUGE_INT = 2 ** 32 - 1
