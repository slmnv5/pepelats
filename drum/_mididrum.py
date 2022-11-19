import time

import mido
import numpy as np

from drum._fakedrum import FakeDrum
from utils import SD_RATE


def int_to_midi(k: int) -> mido.Message:
    byte_str: str = f'{k:028b}'
    byte_lst = [0xF0]
    byte_lst.extend(bytes(int(byte_str[i: i + 7], 2) for i in range(0, len(byte_str), 7)))
    byte_lst.append(0xF7)
    msg = mido.Message.from_bytes(byte_lst)
    print(msg)
    return msg


# noinspection PyUnresolvedReferences
class MidiDrum(FakeDrum):
    def __init__(self):
        super().__init__()
        self.__out_port = mido.open_output("LooperCloc_out")
        self.__sleep_time: float = 3  # sleep time in seconds
        self.__stop: bool = True
        self.__count: int = 0  # midi tick counter - 96 per bar
        self.__idx: int = 0  # loop index
        self.__prev_idx: int = 0  # loop prev index
        self.__time: float  # time tick was sent
        self.__prev_time: float

        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    def __send_tick(self):
        self.__out_port.send(mido.Message.from_bytes([0xF8]))

    def __send_start(self):
        self.__out_port.send(mido.Message.from_bytes([0xFA]))

    def __send_stop(self):
        self.__out_port.send(mido.Message.from_bytes([0xFC]))

    def prepare_drum(self, length: int) -> None:
        self.__sleep_time = length / SD_RATE / 96

    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        self.__idx = idx

    def __send_clock(self):
        while True:
            time.sleep(self.__sleep_time)
            if self.self.__prev_idx == self.__idx:
                self.__stop = True
                self.__send_stop()
                continue

            if self.__stop:
                self.__start = time.monotonic()
                self.__send_start()
                self.__stop = False
            else:
                self.__send_tick()


if __name__ == "__main__":
    def test():
        int_to_midi(100000)


    test()
