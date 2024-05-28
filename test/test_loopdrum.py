import numpy as np
import sounddevice as sd

from drum.drumfactory import create_drum
from song.songpart import SongPart
from utils.utilalsa import make_sin_sound
from audio.audioinfo import AINFO, correct_sound


def test_1():
    sound = make_sin_sound(440, 7)
    sound = correct_sound(sound, AINFO.SD_CH, AINFO.SD_TYPE)
    sp = SongPart()
    sp.record(sound, 0)
    drum = create_drum("LoopDrum")
    drum.songpart = sp
    drum.set_bar_len(100_000)
    drum.start()
    arr = np.zeros((120_000, AINFO.SD_CH), AINFO.SD_TYPE)
    drum.play(arr, 0)
    sd.play(arr, blocking=True)
