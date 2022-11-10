import os
from pathlib import Path

import numpy as np
import sounddevice as sd

ROOT_DIR = Path(__file__).parent.parent

MAX_LATE_SECONDS = os.getenv("MAX_LATE_SECONDS", "0.1")
try:
    MAX_LATE_SECONDS = float(MAX_LATE_SECONDS)
except ValueError:
    MAX_LATE_SECONDS = 0.1

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
    description: str = "description"

    # redraw related methods
    change_map: str = "_change_map"
    send_redraw: str = "_send_redraw"

    #  drum related
    default_pattern: str = "default_pattern"
    comment: str = "comment"

    #  main loader saved values
    drum_type: str = "DRUM_TYPE"
    song_name: str = "SONG_NAME"
    drum_swing: str = "DRUM_SWING"
    drum_volume: str = "DRUM_VOLUME"
    mixer_in: str = "MIXER_IN"
    mixer_out: str = "MIXER_OUT"
