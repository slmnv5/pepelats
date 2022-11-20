import logging
import os
import time
from threading import Thread

import mido
import numpy as np

from drum._fakedrum import FakeDrum
from utils import MockMidiPort
from utils import SD_RATE
from utils import open_midi_port


def int_to_midi(k: int) -> mido.Message:
    byte_str: str = f'{k:028b}'
    byte_lst = [0xF0]
    byte_lst.extend(bytes(int(byte_str[i: i + 7], 2) for i in range(0, len(byte_str), 7)))
    byte_lst.append(0xF7)
    msg = mido.Message.from_bytes(byte_lst)
    print(msg)
    return msg


def bpm_to_bar_seconds(bpm: float) -> float:
    return 60 / bpm * 4


class MidiDrum(FakeDrum):
    ticks_per_bar: int = 96
    __min_sleep_time: float = bpm_to_bar_seconds(280) / ticks_per_bar  # 280 BPM
    __max_sleep_time: float = bpm_to_bar_seconds(40) / ticks_per_bar  # 40 BPM

    def __init__(self):
        super().__init__()
        if os.name != "posix":
            self.__out_port = MockMidiPort()
        else:
            port_name = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
            self.__out_port = open_midi_port(port_name, is_input=True)
            if not self.__out_port:
                msg = f"Failed to open MIDI port for clock output: {port_name}"
                logging.error(msg)
                raise RuntimeError(msg)

        self.__sleep_time: float = 1  # sleep time in seconds
        self.__start: float = 0  # slart time
        self.__upd: float = 100  # update time
        self.__prev_upd: float = 0  # prev update time
        self.__is_stop: bool = True
        self.__chunk_len: int = 0  # numpy array length
        self.__count: int = 0  # midi tick counter - 96 per bar

        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    def get_fixed(self) -> str:
        return "MIDI"

    def __send_tick(self):
        self.__out_port.send(mido.Message.from_bytes([0xF8]))

    def __send_start(self):
        if not self.__is_stop:
            return
        self.__start_at = time.monotonic()
        self.__is_stop = False
        self.__out_port.send(mido.Message.from_bytes([0xFA]))

    def __send_stop(self):
        if self.__is_stop:
            return
        self.__is_stop = True
        self.__out_port.send(mido.Message.from_bytes([0xFC]))

    def prepare_drum(self, length: int) -> None:
        self.__sleep_time = length / SD_RATE / MidiDrum.ticks_per_bar
        self.__sleep_time = max(self.__sleep_time, MidiDrum.__min_sleep_time)
        self.__chunk_len = 0

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if not self.__chunk_len:
            self.__chunk_len = len(out_data)
        self.__prev_upd = self.__upd
        self.__upd = time.monotonic()

    def __send_clock(self):
        self.__out_port.send(mido.Message.from_bytes([0xFC]))
        self.__out_port.send(mido.Message.from_bytes([0xFC]))
        self.__out_port.send(mido.Message.from_bytes([0xFC]))
        while True:
            time.sleep(self.__sleep_time)
            stopped: bool = self.__upd - self.__prev_upd > MidiDrum.__max_sleep_time
            if stopped:
                self.__send_stop()
            else:
                self.__send_start()
                self.__send_tick()


if __name__ == "__main__":
    def test():
        from loop._loopsimple import LoopWithDrum
        from loop._oneloopctrl import OneLoopCtrl

        drum = MidiDrum()
        drum.prepare_drum(100_000)
        assert bpm_to_bar_seconds(80) == 3
        ctrl = OneLoopCtrl(drum)
        loop = LoopWithDrum(ctrl, 200_000)
        loop.play_buffer()
        print(bpm_to_bar_seconds(40) / MidiDrum.ticks_per_bar)
        print(bpm_to_bar_seconds(280) / MidiDrum.ticks_per_bar)


    test()
