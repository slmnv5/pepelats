import sounddevice as sd

from utils.utilalsa import make_zero_buffer
from utils.utilfactory import create_drum


def test_1():
    drum = create_drum("PatternDrum")
    drum.start()
    drum.set_config("Test.ini")
    arr = make_zero_buffer(150_000)

    drum.set_bar_len(300_000)

    drum.set_par(0)
    drum.play(arr, 0)
    sd.play(arr, blocking=True)

    drum.set_par(1)
    drum.play(arr, 0)
    sd.play(arr, blocking=True)
