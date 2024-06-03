import os
import sys
from configparser import ConfigParser

from utils.utillog import MYLOG

APP_DIR = os.sep + 'pepelats'


class ConfigName:
    # menu and midi config related
    drum_create: str = "_drum_create"
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
    midi_min_velocity: str = "midi_min_velocity"
    max_len_seconds: str = "max_len_seconds"
    device_name: str = "device_name"
    device_type: str = "device_type"
    kbd_notes_linux: str = "kbd_notes_linux"
    kbd_notes_windows: str = "kbd_notes_windows"
    kbd_notes_midi: str = "kbd_notes_midi"
    # drum config
    drum_config: str = 'drum_config'
    drum_volume: str = "drum_volume"
    drum_par: str = "drum_par"
    drum_song_part: str = "drum_song_part"
    # drum types
    EuclidPtrnDrum: str = "EuclidPtrnDrum"
    OldPtrnDrum: str = "OldPtrnDrum"
    MidiDrum: str = "MidiDrum"
    LoopDrum: str = "LoopDrum"
    SilentDrum: str = "SilentDrum"


def find_path(path_end: str) -> str:
    """Find file or dir. creates one if missing"""
    tmp1 = os.getcwd() + os.sep + path_end
    pos = tmp1.find(APP_DIR)
    if pos >= 0:
        return tmp1[:pos + len(APP_DIR)] + os.sep + path_end
    else:
        MYLOG.error(f"Path not found: {path_end}")
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
SD_RATE: int = 44100
HUGE_INT = 2 ** 32 - 1

try:
    _max_sec = int(load_ini_section("AUDIO")['max_len_seconds'])
except Exception as ex:
    MYLOG.exception(ex)
    _max_sec = 60

MAX_LEN = _max_sec * SD_RATE
MYLOG.warning(f"Set sampling rate: {SD_RATE}, max. loop length: {_max_sec} sec")
