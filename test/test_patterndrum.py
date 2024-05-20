import sounddevice as sd

from utils.utilalsa import make_zero_buffer
from utils.utilfactory import create_drum


def test_1():
    dr = create_drum("PatternDrum")
    dr.start()
    dr.set_config("Test.ini")
    arr = make_zero_buffer(150_000)

    dr.load_config(300_000)

    dr.set_par(0)
    dr.play(arr, 0)
    sd.play(arr, blocking=True)

    dr.set_par(1)
    dr.play(arr, 0)
    sd.play(arr, blocking=True)
