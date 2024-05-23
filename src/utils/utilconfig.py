import os
import sys
from configparser import ConfigParser

import numpy as np
import sounddevice as sd

from utils.utillog import get_my_log

APPDIR = os.sep + os.environ['APPDIR']

my_log = get_my_log(__name__)


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


_audio: dict[str, str] = load_ini_section(find_path(ConfigName.main_ini), "AUDIO")
pref_lst: list[str] = _audio.get("preffered_list", "USB Audio").split(",")
assert pref_lst and isinstance(pref_lst[0], str)
found_dev: bool = False
for pref_name in pref_lst:
    if found_dev:
        break
    for idx, dev in enumerate(sd.query_devices()):
        if pref_name.strip().upper() in dev.get("name").upper():
            sd.default.device = (idx, idx)
            my_log.info(f"Found preferred device provided in main.ini - {pref_name}")
            found_dev = True

dev_in: dict[str, any] = sd.query_devices(sd.default.device[0])
dev_out: dict[str, any] = sd.query_devices(sd.default.device[1])
my_log.info(f"Using IN device {dev_in['name']}")
my_log.info(f"Using OUT device {dev_out['name']}")

OUT_CH = dev_out["max_output_channels"]
IN_CH = dev_in["max_input_channels"]
if IN_CH not in [1, 2]:
    raise RuntimeError(f"ALSA IN device must have 1 or 2 channels, got {IN_CH}")
if OUT_CH not in [1, 2]:
    raise RuntimeError(f"ALSA OUT device must have 1 or 2 channels, got {OUT_CH}")

IN_CH = OUT_CH = min(IN_CH, OUT_CH)

SD_TYPE: str = _audio.get('sd_type', "int16")
assert SD_TYPE and isinstance(SD_TYPE, str)

MAX_LEN_SECONDS: int = int(_audio.get('max_len_seconds', 60))
assert MAX_LEN_SECONDS and isinstance(MAX_LEN_SECONDS, int)

SD_RATE: int = int(_audio.get('sd_rate', 44100))
assert SD_RATE and isinstance(SD_RATE, int)

MAX_SD_TYPE = np.iinfo(SD_TYPE).max
MAX_LEN: int = MAX_LEN_SECONDS * SD_RATE
MAX_32_INT = np.iinfo(np.int32).max  # 2 ** 32 - 1

sd.default.samplerate = SD_RATE
sd.default.dtype = [SD_TYPE, SD_TYPE]
sd.default.latency = ('low', 'low')
sd.default.channels = IN_CH, OUT_CH

sd.check_output_settings(channels=OUT_CH, dtype=SD_TYPE, samplerate=SD_RATE)
sd.check_input_settings(channels=IN_CH, dtype=SD_TYPE, samplerate=SD_RATE)

_keyboard = load_ini_section(find_path(ConfigName.main_ini), "KEYBOARD")
tmp = _keyboard.get('kbd_notes_windows', '1,2,3,4,q,w')
tmp = [x.strip() for x in tmp.split(',')]
if len(tmp) != 6:
    raise RuntimeError(f"kbd_notes_windows in main.ini must have at 6 keys, found: {tmp}")
KBD_NOTES: list[str] = tmp

tmp = _keyboard.get('kbd_notes_linux', KBD_NOTES)
tmp = [x.strip() for x in tmp.split(',')]
if len(tmp) != 6:
    raise RuntimeError(f"kbd_notes_windows in main.ini must have 6 keys, found: {tmp}")
KBD_NOTES_LINUX: list[str] = tmp

tmp = _keyboard.get('midi_notes', '60,62,64,65,12,13')
tmp = [x.strip() for x in tmp.split(',')]
# noinspection PyBroadException
try:
    tmp = [int(x) for x in tmp]
except Exception:
    pass

if len(tmp) != 6:
    raise RuntimeError(f"midi_notes in main.ini must have 6 values, found: {tmp}")
if not all(isinstance(x, int) and 0 <= x <= 127 for x in tmp):
    raise RuntimeError(f"midi_notes in main.ini must have integer values [0:127], found: {tmp}")

MIDI_NOTES: list[int] = tmp

_screen = load_ini_section(find_path(ConfigName.main_ini), "SCREEN")
KEEP_SCREEN = "--keep_screen" in sys.argv

# min note velocity to consider, conted notes have velocity equal to count
MIN_VELO: int = 10
# standard note velocity, note loder than MIN_VELO is converted to STD_VELO
STD_VELO: int = 100
