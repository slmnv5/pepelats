import os
from pathlib import Path

import numpy as np
import sounddevice as sd

ROOT_DIR = str(Path(__file__).parent.parent.parent)

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
    shared_lib: str = "touchscr5.so"

    # redraw related methods
    change_map: str = "_change_map"
    send_redraw: str = "_send_redraw"
    kill_app: str = "_kill_app"
