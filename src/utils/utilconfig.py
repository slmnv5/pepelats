import os
import sys
from configparser import ConfigParser

from utils.utillog import MYLOG

APPDIR = os.sep + 'pepelats'


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
    midi_out: str = "midi_out"
    midi_in: str = "midi_in"
    midi_min_velocity: str = "midi_min_velocity"
    max_len_seconds: str = "max_len_seconds"
    device_name: str = "device_name"
    device_type: str = "device_type"
    kbd_notes_linux: str = "kbd_notes_linux"
    kbd_notes_windows: str = "kbd_notes_windows"
    kbd_midi_notes: str = "kbd_midi_notes"
    # drum config
    drum_config: str = 'drum_config'
    drum_volume: str = "drum_volume"
    drum_par: str = "drum_par"
    drum_part_idx: str = "drum_part_idx"
    drum_songpart: str = "drum_songpart"
    # drum types
    EuclidPtrnDrum: str = "EuclidPtrnDrum"
    OldPtrnDrum: str = "OldPtrnDrum"
    MidiDrum: str = "MidiDrum"
    LoopDrum: str = "LoopDrum"
    SilentDrum: str = "SilentDrum"


def find_path(path_end: str) -> str:
    """Find file or dir. creates one if missing"""
    tmp1 = os.getcwd() + os.sep + path_end
    pos = tmp1.find(APPDIR)
    if pos >= 0:
        return tmp1[:pos + len(APPDIR)] + os.sep + path_end
    else:
        MYLOG.error(f"Path not found: {path_end}")
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


KEEP_SCREEN: bool = "--keep_screen" in sys.argv
SD_RATE: int = 44100
HUGE_INT = 2 ** 32 - 1

try:
    _max_sec = int(load_ini_section(find_path(ConfigName.main_ini), "AUDIO")['max_len_seconds'])
except Exception as ex:
    MYLOG.exception(ex)
    _max_sec = 60

MAX_LEN = _max_sec * SD_RATE
MYLOG.warning(f"Set sampling rate: {SD_RATE}, max. loop length: {_max_sec} sec")
