import json
import logging
from typing import Optional

import numpy as np
import rtmidi
import sounddevice as sd
from rtmidi.midiutil import open_midiinput, open_midioutput

from utils.utilconfig import SD_TYPE, MAX_LEN, USB_AUDIO_NAMES, PEDAL_PORT_NAME, CLOCK_PORT_NAME


def get_midi_in() -> Optional[rtmidi.MidiIn]:
    # noinspection PyBroadException
    try:
        midi_in, _ = open_midiinput(PEDAL_PORT_NAME, interactive=False)  # may throw
        return midi_in
    except Exception:
        logging.error(f"Cannot open port MIDI IN: {PEDAL_PORT_NAME}")
        return None


def get_midi_out() -> Optional[rtmidi.MidiOut]:
    # noinspection PyBroadException
    try:
        midi_out, _ = open_midioutput(CLOCK_PORT_NAME, interactive=False)
        return midi_out
    except Exception:
        logging.error(f"Cannot open port MIDI OUT: {CLOCK_PORT_NAME}")
        return None


def find_usb() -> None:
    """Look for USB Audio device and set it default"""

    try:
        new_str = USB_AUDIO_NAMES.strip(' ,').replace("'", "").replace('"', '').replace(',', '","')
        usb_audio = json.loads(f'["{new_str}"]')
    except Exception as err:
        msg = f"Failed to parse env. variable USB_AUDIO_NAMES, error: {err}"
        raise RuntimeError(msg)

    all_devices = sd.query_devices()
    for k, dev in enumerate(all_devices):
        for sd_name in usb_audio:
            full_name = dev["name"]
            if sd_name in full_name:
                logging.info(f"Found requested device {sd_name} in {full_name}")
                sd.default.device = k, k
                return
    logging.error(f"Not found requested device: {usb_audio}")


find_usb()

IN_CH = sd.query_devices(sd.default.device[0])["max_input_channels"]
OUT_CH = sd.query_devices(sd.default.device[1])["max_output_channels"]
if OUT_CH != 2:
    raise RuntimeError(f"ALSA audio device must have 2 output channels, got {OUT_CH}")
if IN_CH not in [1, 2]:
    raise RuntimeError(f"ALSA audio device must have 1 or 2 input channels, got {IN_CH}")


def make_zero_buffer(buff_len: int) -> np.ndarray:
    if buff_len < 0 or buff_len > MAX_LEN:
        raise ValueError(f"make_zero_buffer() incorrect parameter: {buff_len}")
    return np.zeros((buff_len, 2), SD_TYPE)


def make_sin_sound(sound_freq: int, duration_sec: float, amplitude: int = 3000) -> np.ndarray:
    points_in_array = int(sd.default.samplerate * duration_sec)
    t = np.linspace(0, duration_sec, points_in_array)
    x = amplitude * np.sin(2 * np.pi * sound_freq * t)
    x = x.astype("int16")[:, np.newaxis]
    x = np.column_stack((x, x))
    return x


def make_changing_sound() -> np.ndarray:
    a = make_sin_sound(330, 0.3)
    b = make_sin_sound(550, 0.3)
    return np.concatenate((a, b, a), axis=0)


if __name__ == "__main__":
    pass
