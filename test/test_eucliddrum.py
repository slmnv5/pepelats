import sounddevice

from utils.utilalsa import make_zero_buffer
from utils.utilfactory import create_drum


def test_1():
    dr = create_drum("EuclidDrum")
    dr.load_drum_config(None, 100_000)
    dr.start_drum()
    arr = make_zero_buffer(120_000)
    dr.play_drums(arr, 0)
    sounddevice.play(arr, blocking=True)
