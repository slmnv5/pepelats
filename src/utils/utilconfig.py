import os
import sys
from pathlib import Path

import numpy as np
import sounddevice as sd

ENV_DRUM_CHANNEL: int = int(os.getenv("DRUM_CHANNEL", "9"))
ENV_KBD_NOTES: str = os.getenv("KBD_NOTES", '"q": 12, "w": 13, "1":60, "2": 62, "3": 64, "4": 65')
ENV_LEN_SECONDS = os.getenv("MAX_LEN_SECONDS", "60")
ENV_SD_RATE: int = int(os.getenv("SD_RATE", "44100"))
ENV_FRAME_BUFFER_ID: str = os.getenv("FRAME_BUFFER_ID", "1")
ENV_USB_AUDIO_NAMES: str = os.getenv("USB_AUDIO_NAMES", "USB Audio")
ENV_MIDI_IN_PORT = os.getenv('MIDI_IN_PORT_NAME', "MidiPedal_out")
ENV_MIDI_OUT_PORT = os.getenv('MIDI_OUT_PORT_NAME', "MidiDrum_in")

ROOT_DIR = str(Path(__file__).parent.parent.parent)
LEVEL_DEBUG = "--debug" in sys.argv or "--info" in sys.argv or os.name != "posix"
SD_TYPE: str = 'int16'
MAX_LEN: int = int(ENV_LEN_SECONDS) * ENV_SD_RATE
MAX_32_INT = 2 ** 32 - 1
SD_MAX: int = np.iinfo(SD_TYPE).max

sd.default.samplerate = ENV_SD_RATE
sd.default.dtype = [SD_TYPE, SD_TYPE]
sd.default.latency = ('low', 'low')


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


def save_config() -> None:
    file_name = ROOT_DIR + "/.saved_env.sh"
    with open(file_name, 'w') as f:
        f.write(f"export ENV_DRUM_CHANNEL='{ENV_DRUM_CHANNEL}'\n")
        f.write(f"export ENV_KBD_NOTES='{ENV_KBD_NOTES}'\n")
        f.write(f"export ENV_LEN_SECONDS='{ENV_LEN_SECONDS}'\n")
        f.write(f"export ENV_SD_RATE='{ENV_SD_RATE}'\n")
        f.write(f"export ENV_FRAME_BUFFER_ID='{ENV_FRAME_BUFFER_ID}'\n")
        f.write(f"export ENV_USB_AUDIO_NAMES='{ENV_USB_AUDIO_NAMES}'\n")
        f.write(f"export ENV_MIDI_IN_PORT='{ENV_MIDI_IN_PORT}'\n")
        f.write(f"export ENV_MIDI_OUT_PORT='{ENV_MIDI_OUT_PORT}'\n")

    f.close()
