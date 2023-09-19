import os
import sys
from configparser import ConfigParser

import numpy as np
import sounddevice

APP_DIR = os.sep + "pepeloop"


def find_path(path_end: str) -> str:
    """Find file or dir. creates one if missing"""
    tmp = os.getcwd() + os.sep + path_end
    if os.path.exists(tmp):
        return tmp
    pos = tmp.find(APP_DIR)
    if pos >= 0:
        return tmp[:pos + len(APP_DIR)] + os.sep + path_end
    else:
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


def get_file_name(self) -> str:
    return self._fname


_audio = load_ini_section(find_path("main.ini"), "AUDIO")

SD_TYPE = _audio.get('sd_type')
MAX_LEN_SECONDS = int(_audio.get('max_len_seconds'))
SD_RATE = int(_audio.get('sd_rate'))

_keyboard = load_ini_section(find_path("main.ini"), "KEYBOARD")
KBD_NOTES = _keyboard.get('kbd_notes')
_screen = load_ini_section(find_path("main.ini"), "SCREEN")
FRAME_BUFFER_ID = _audio.get('frame_buffer_id')
VERBOSE_MODE = "--debug" in sys.argv or "--info" in sys.argv
KEEP_SCREEN = "--keep_screen" in sys.argv

MAX_SD_TYPE = np.iinfo(SD_TYPE).max
MAX_LEN: int = MAX_LEN_SECONDS * SD_RATE
MAX_32_INT = np.iinfo(np.int32).max  # 2 ** 32 - 1

OUT_CH = 2
IN_CH = sounddevice.query_devices(sounddevice.default.device[0])["max_input_channels"]
if IN_CH not in [1, 2]:
    raise RuntimeError(f"ALSA audio device must have 1 or 2 input channels, got {IN_CH}")

sounddevice.check_output_settings(channels=OUT_CH, dtype=SD_TYPE, samplerate=SD_RATE)
sounddevice.check_input_settings(channels=IN_CH, dtype=SD_TYPE, samplerate=SD_RATE)

sounddevice.default.samplerate = SD_RATE
sounddevice.default.dtype = [SD_TYPE, SD_TYPE]
sounddevice.default.latency = ('low', 'low')


class ConfigName:
    # menu and midi config related
    default_config: str = "default_config"
    update_method: str = "update_method"
    description: str = "description"
    comment: str = "comment"
    shared_lib: str = "touchscreen4py.so"
    client_redraw: str = "_redraw"  # this is MenuClient command to update screen
