import json
import logging
import os
from typing import Union

import numpy as np
import rtmidi
import sounddevice as sd
from rtmidi.midiutil import open_midiinput, open_midioutput

from utils._utilnumpy import calc_slices
from utils.config import SD_TYPE, MAX_LEN
from utils.utilport import MyRtmidi, FakePort


def get_midi_in() -> MyRtmidi:
    port_name = os.getenv('PEDAL_PORT_NAME', "PedalCommands_out")
    midi_in, _ = open_midiinput(port_name, interactive=False)  # may throw
    return MyRtmidi(midi_in)  # adapter classs


def get_midi_out() -> Union[rtmidi.MidiOut, FakePort]:
    port_name = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
    # noinspection PyBroadException
    try:
        midi_out, _ = open_midioutput(port_name, interactive=False)
        return midi_out
    except Exception:
        logging.error(f"Cannot open port for MIDI output: {port_name}, using FakePort")
        return FakePort()


def find_usb() -> None:
    """Look for USB Audio device and set it default"""
    usb_audio_str: str = os.getenv("USB_AUDIO_NAMES", "USB Audio")

    try:
        new_str = usb_audio_str.strip(' ,').replace("'", "").replace('"', '').replace(',', '","')
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


def record_sound_buff(buff: np.ndarray, np_data: np.ndarray, idx: int) -> None:
    assert buff.ndim == np_data.ndim
    data_len = len(np_data)
    if IN_CH == 1:
        np_data = np.broadcast_to(np_data, (data_len, 2))
    slice1, slice2 = calc_slices(len(buff), data_len, idx)
    if slice2 is None:
        buff[slice1] += np_data[:]
    else:
        s1 = slice1.stop - slice1.start
        s2 = slice2.stop - slice2.start
        buff[slice1] += np_data[0:s1]
        buff[slice2] += np_data[s1:s1 + s2]


def play_sound_buff(buff: np.ndarray, np_data: np.ndarray, idx: int) -> None:
    assert type(buff) == type(np_data), f"{type(buff)}, {type(np_data)}"
    assert buff.ndim == np_data.ndim
    data_len = len(np_data)
    slice1, slice2 = calc_slices(len(buff), data_len, idx)
    if slice2 is None:
        np_data[:] += buff[slice1]
    else:
        s1 = slice1.stop - slice1.start
        np_data[:s1] += buff[slice1]
        np_data[s1:] += buff[slice2]


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
    def run():
        print("=========================")
        print(sd.query_devices())
        print("=========================")

        print("=========================")
        print(sd.query_devices(sd.default.device[0]))
        print(sd.query_devices(sd.default.device[1]))
        print("=========================")


    run()
