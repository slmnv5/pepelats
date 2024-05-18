import sounddevice as sd

from utils.utilalsa import make_zero_buffer
from utils.utilfactory import create_drum


def test_1():
    dr = create_drum("PatternDrum")
    dr.start_drum()
    arr = make_zero_buffer(120_000)

    dr.load_drum_config("Test", 100_000)

    dr.set_par(0)
    print(111111111111111, str(dr))
    dr.play_drums(arr, 0)
    sd.play(arr, blocking=True)

    dr.set_par(1)
    print(111111111111111, str(dr))
    dr.play_drums(arr, 0)
    sd.play(arr, blocking=True)
