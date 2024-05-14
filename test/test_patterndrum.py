import sounddevice as sd

from utils.utilalsa import make_zero_buffer
from utils.utilfactory import create_drum


def test_1():
    dr = create_drum("PatternDrum")
    dr.start_drum()
    dr.load_drum_config(None, 100_000)
    arr = make_zero_buffer(120_000)
    dr.play_drums(arr, 0)
    sd.play(arr, blocking=True)
