import sounddevice

from song.songpart import SongPart
from utils.utilalsa import make_zero_buffer, make_sin_sound, correct_dtype
from utils.utilfactory import get_drum


def test_1():
    sound = make_sin_sound(440, 7)
    sound = correct_dtype(sound)
    sp = SongPart()
    sp._record_samples(sound, 0)
    kwargs = {"SongPart": sp}
    dr = get_drum("LoopDrum", **kwargs)
    dr.load_drum_config(None, 100_000)
    arr = make_zero_buffer(120_000)
    dr.play_drums(arr, 0)
    sounddevice.play(arr, blocking=True)
