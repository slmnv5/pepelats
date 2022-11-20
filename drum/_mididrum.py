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


TICKS_PER_BAR: int = 96
MIN_SLEEP: float = bpm_to_bar_seconds(280) / TICKS_PER_BAR  # 280 BPM
MAX_SLEEP: float = bpm_to_bar_seconds(40) / TICKS_PER_BAR  # 40 BPM


class MidiDrum(FakeDrum):

    def __init__(self):
        super().__init__()
        if os.name != "posix":
            self.__out_port = MockMidiPort()
        else:
            port_name = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
            self.__out_port = open_midi_port(port_name, is_input=False)
            if not self.__out_port:
                msg = f"Failed to open MIDI port for clock output: {port_name}"
                logging.error(msg)
                raise RuntimeError(msg)

        self.__sleep_time: float = 1  # sleep time in seconds
        self.__start_at: float = 0  # slart time
        self.__upd: float = time.monotonic()  # update time
        self.__prev_upd: float = time.monotonic()  # prev update time
        self.__chunk_len: int = 0  # numpy array length
        self.__count: int = 0  # midi tick counter - 96 per bar

        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    def get_fixed(self) -> str:
        return "MIDI"

    def __send_tick(self):
        self.__out_port.send(mido.Message.from_bytes([0xF8]))

    def __send_start(self):
        if self.__start_at:
            return
        self.__start_at = time.monotonic()
        self.__out_port.send(mido.Message.from_bytes([0xFA]))

    def __send_stop(self):
        if self.__start_at:
            self.__start_at = 0
            self.__out_port.send(mido.Message.from_bytes([0xFC]))

    def prepare_drum(self, length: int) -> None:
        self.__sleep_time = length / SD_RATE / TICKS_PER_BAR
        self.__sleep_time = max(self.__sleep_time, MIN_SLEEP)
        self.__chunk_len = 0

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        if not self.__chunk_len:
            self.__chunk_len = len(out_data)
        self.__prev_upd = self.__upd
        self.__upd = time.monotonic()

    def __send_clock(self):
        while True:
            time.sleep(self.__sleep_time)
            diff = self.__upd - self.__prev_upd
            print(111111111, diff, self.__start_at)
            if diff > MAX_SLEEP:
                self.__send_stop()
            else:
                self.__send_start()
                self.__send_tick()


if __name__ == "__main__":
    def test():
        from loop._loopsimple import LoopWithDrum
        from loop._oneloopctrl import OneLoopCtrl
        from threading import Timer

        print(bpm_to_bar_seconds(40) / TICKS_PER_BAR)
        print(bpm_to_bar_seconds(280) / TICKS_PER_BAR)

        drum = MidiDrum()
        drum.prepare_drum(100_000)
        assert bpm_to_bar_seconds(80) == 3
        ctrl = OneLoopCtrl(drum)
        loop = LoopWithDrum(ctrl, 200_000)
        Timer(0.8, ctrl.stop_at_bound, [0]).start()
        loop.play_buffer()
        time.sleep(1)


    test()
