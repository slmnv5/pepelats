import mido

from drum._fakedrum import FakeDrum


# noinspection PyMethodMayBeStatic
class MidiDrum(FakeDrum):
    def __init__(self):
        self.__out_port = mido.open_output("pepelats_cloc")
        pass
