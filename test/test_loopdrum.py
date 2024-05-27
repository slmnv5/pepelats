import sounddevice as sd

from drum.drumfactory import create_drum
from song.songpart import SongPart
from utils.utilalsa import make_zero_buffer, make_sin_sound
from utils.utilaudio import AUDIO, correct_sound


def test_1():
    sound = make_sin_sound(440, 7)
    sound = correct_sound(sound, AUDIO.SD_CH, AUDIO.SD_TYPE)
    sp = SongPart()
    sp.record_samples(sound, 0)
    drum = create_drum("LoopDrum")
    drum.songpart = sp
    drum.set_bar_len(100_000)
    drum.start()
    arr = make_zero_buffer(120_000)
    drum.play(arr, 0)
    sd.play(arr, blocking=True)
