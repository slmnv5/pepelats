import logging
import os
import time
from threading import Thread

import mido
import numpy as np

from drum._fakedrum import FakeDrum
from utils import MockMidiPort, make_sin_sound
from utils import SD_RATE
from utils import open_midi_port


def int_to_midi(k: int) -> mido.Message:
    byte_str: str = f'{k:028b}'
    byte_lst = [0xF0]
    byte_lst.extend(bytes(int(byte_str[i: i + 7], 2) for i in range(0, len(byte_str), 7)))
    byte_lst.append(0xF7)
    msg = mido.Message.from_bytes(byte_lst)
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
        self.__upd: float = 0  # update time
        self.__length: int = 0

        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    def get_fixed(self) -> str:
        return "MIDI"

    def get_length(self) -> int:
        return self.__length

    def __send_tick(self):
        self.__out_port.send(mido.Message.from_bytes([0xF8]))

    def prepare_drum(self, length: int) -> None:
        self.__length: int = length
        self.__start_at = 0
        self.__out_port.send(mido.Message.from_bytes([0xFC]))
        self.__sleep_time = length / SD_RATE / TICKS_PER_BAR
        self.__sleep_time = max(self.__sleep_time, MIN_SLEEP)

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self.__upd = time.monotonic()

    def __send_clock(self):
        while True:
            time.sleep(self.__sleep_time)
            now = time.monotonic()
            diff = now - self.__upd
            if diff > MAX_SLEEP:
                if self.__start_at:
                    self.__start_at = 0
                    self.__out_port.send(mido.Message.from_bytes([0xFC]))
            else:
                if not self.__start_at:
                    self.__start_at = now
                    self.__out_port.send(mido.Message.from_bytes([0xFA]))

                self.__send_tick()


if __name__ == "__main__":
    def test():
        from loop._loopsimple import LoopWithDrum
        from loop._oneloopctrl import OneLoopCtrl
        from threading import Timer
        # from drum import RealDrum

        sound = make_sin_sound(440, 7.1)
        drum = MidiDrum()
        drum.prepare_drum(100_000)
        while not drum.get_length():
            time.sleep(0.1)

        ctrl = OneLoopCtrl(drum)
        loop = LoopWithDrum(ctrl)
        loop.record_samples(sound, 200_000)  # record in the middle of loop

        print("======== start =============")
        loop.trim_buffer(500_000)
        Timer(3, ctrl.stop_at_bound, [0]).start()
        loop.play_buffer()


    test()
