import time

import mido

from drum._fakedrum import FakeDrum


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
    def __int__(self):
        super().__init__()
        self.__out_port = mido.open_output("LooperCloc_out")
        self.__sleep_time: float = 3  # sleep time in seconds
        self.__count: int = 0  # midi tick counter - 96 per bar
        self.__idx: int = 0  # loop index
        self.__prev_idx: int = 0  # loop prev index
        Thread(target=self.__send_clock, name="send_clock_thread", daemon=True).start()

    def __send_tick(self):
        pass

    def prepare_drum(self, length: int) -> None:
        delta = length / SD_RATE
        print(delta)
        pass

    def __send_clock(self):
        while True:
            time.sleep(self.__sleep_time)
            if self.self.__prev_idx == self.__idx:
                continue
            self.__send_tick()


if __name__ == "__main__":
    def test():
        int_to_midi(100000)


    test()
