import os
import time
from threading import Thread

import mido
import numpy as np

from drum._fakedrum import FakeDrum
from utils._utilalsa import MockMidiPort
from utils import SD_RATE


def int_to_midi(k: int) -> mido.Message:
    byte_str: str = f'{k:028b}'
    byte_lst = [0xF0]
    byte_lst.extend(bytes(int(byte_str[i: i + 7], 2) for i in range(0, len(byte_str), 7)))
    byte_lst.append(0xF7)
    msg = mido.Message.from_bytes(byte_lst)
    print(msg)
    return msg


class MidiDrum(FakeDrum):
    __ticks_per_bar: int = 96
    __min_sleep_time: float = 0.86 / __ticks_per_bar

    def __init__(self):
        super().__init__()
        if os.name != "posix":
            self.__out_port = MockMidiPort()
        else:
            # noinspection PyUnresolvedReferences
            self.__out_port = mido.open_output("LooperCloc_out", virtual=True)

        self.__sleep_time: float = 3  # sleep time in seconds
        self.__start_at: float = 0  # slarted at time
        self.__is_stop: bool = True
        self.__count: int = 0  # midi tick counter - 96 per bar
        self.__idx: int = 0  # loop index
        self.__prev_idx: int = 0  # loop prev index

        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    def get_fixed(self) -> str:
        return "MIDI"

    def __send_tick(self):
        self.__out_port.send(mido.Message.from_bytes([0xF8]))

    def __send_start(self):
        self.__is_stop = False
        self.__start_at = time.monotonic()
        self.__out_port.send(mido.Message.from_bytes([0xFA]))

    def __send_stop(self):
        self.__is_stop = True
        self.__out_port.send(mido.Message.from_bytes([0xFC]))

    def prepare_drum(self, length: int) -> None:
        self.__sleep_time = length / SD_RATE / MidiDrum.__ticks_per_bar
        self.__sleep_time = max(self.__sleep_time, MidiDrum.__min_sleep_time)

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self.__prev_idx = self.__idx
        self.__idx = idx

    def __send_clock(self):
        while True:
            time.sleep(self.__sleep_time)
            if self.__prev_idx == self.__idx:
                if not self.__is_stop:
                    self.__send_stop()
            else:
                if self.__is_stop:
                    self.__send_start()

            if not self.__is_stop:
                self.__send_tick()


if __name__ == "__main__":
    def test():
        int_to_midi(100000)
        drum = MidiDrum()
        drum.prepare_drum(100000)


    test()
