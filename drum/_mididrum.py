import mido

from drum._fakedrum import FakeDrum


def int_to_midi(k: int) -> mido.Message:
    byte_str: str = f'{k:028b}'
    byte_lst = [0xF0]
    byte_lst.extend(bytes(int(byte_str[i: i + 7], 2) for i in range(0, len(byte_str), 7)))
    byte_lst.append(0xF7)
    print(byte_lst)
    mido.Message.from_bytes(byte_lst)


# noinspection PyUnresolvedReferences
class MidiDrum(FakeDrum):
    def __init__(self):
        self.__out_port = mido.open_output("pepelats_cloc")
        pass


if __name__ == "__main__":
    def test():
        int_to_midi(100000)


    test()
