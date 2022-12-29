import json
import logging
from typing import Optional

import numpy as np
import rtmidi
import sounddevice as sd
from rtmidi.midiutil import open_midiinput, open_midioutput

from utils._utilnumpy import calc_slices
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


def record_sound_buff(buff: np.ndarray, data: np.ndarray, idx: int) -> None:
    """ insert data into buff starting with idx """
    assert buff.ndim == data.ndim
    data_len = len(data)
    if IN_CH == 1:
        data = np.broadcast_to(data, (data_len, 2))
    slice1, slice2 = calc_slices(len(buff), data_len, idx)
    if slice2 is None:
        buff[slice1] += data[:]
    else:
        s1 = slice1.stop - slice1.start
        s2 = slice2.stop - slice2.start
        buff[slice1] += data[0:s1]
        buff[slice2] += data[s1:s1 + s2]


def play_sound_buff(buff: np.ndarray, data: np.ndarray, idx: int) -> None:
    """ insert buff into data starting with idx """
    assert type(buff) == type(data), f"{type(buff)}, {type(data)}"
    assert buff.ndim == data.ndim
    data_len = len(data)
    slice1, slice2 = calc_slices(len(buff), data_len, idx)
    if slice2 is None:
        data[:] += buff[slice1]
    else:
        s1 = slice1.stop - slice1.start
        data[:s1] += buff[slice1]
        data[s1:] += buff[slice2]


def make_zero_buffer(buff_len: int) -> np.ndarray:
    if buff_len < 0 or buff_len > MAX_LEN:
        raise ValueError(f"make_zero_buffer() incorrect parameter: {buff_len}")
    return np.zeros((buff_len, 2), SD_TYPE)


def sound_test(buffer: np.ndarray, duration_sec: float, record: bool) -> None:
    assert buffer.ndim == 2 and buffer.shape[1] == 2, "Buffer for playback must have 2 channels"
    idx = 0

    # noinspection PyUnusedLocal
    def callback(in_data, out_data, frame_count, time_info, status):
        nonlocal idx

        out_data[:] = 0
        assert len(out_data) == len(in_data) == frame_count
        play_sound_buff(buffer, out_data, idx)
        if record:
            record_sound_buff(buffer, in_data, idx)
        idx += frame_count

    with sd.Stream(callback=callback, dtype=buffer.dtype):
        sd.sleep(int(duration_sec * 1000))


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
