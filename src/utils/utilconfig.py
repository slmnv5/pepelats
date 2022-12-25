import os
import sys
from pathlib import Path

import numpy as np
import sounddevice as sd

ROOT_DIR = str(Path(__file__).parent.parent.parent)

DRUM_CHANNEL: int = int(os.getenv("DRUM_CHANNEL", "9"))
KBD_NOTES: str = os.getenv("KBD_NOTES", '"q": 12, "w": 13, "1":60, "2": 62, "3": 64, "4": 65')
FRAME_BUFFER_ID: str = os.getenv("FRAME_BUFFER_ID", "1")
USB_AUDIO_NAMES: str = os.getenv("USB_AUDIO_NAMES", "USB Audio")
PEDAL_PORT_NAME = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
CLOCK_PORT_NAME = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
SHOW_ERRORS = "--debug" in sys.argv or "--info" in sys.argv or os.name != "posix"

SD_RATE: int = int(os.getenv("SD_RATE", "44100"))
sd.default.samplerate = SD_RATE
SD_TYPE: str = 'int16'
sd.default.dtype = [SD_TYPE, SD_TYPE]
sd.default.latency = ('low', 'low')
MAX_LEN: int = int(os.getenv("MAX_LEN_SECONDS", "60")) * SD_RATE
MAX_32_INT = 2 ** 32 - 1
SD_MAX: int = np.iinfo(SD_TYPE).max


class ConfigName:
    # menu and midi config related
    default_config: str = "default_config"
    update_method: str = "update_method"
    text: str = "description"
    comment: str = "comment"
    shared_lib: str = "touchscreen4py.so"

    # redraw related methods
    change_map: str = "_change_map"
    send_redraw: str = "_send_redraw"
    restart_looper: str = "_restart_looper"
