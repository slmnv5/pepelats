from multiprocessing import Queue
from threading import Timer

from song.loopsimple import LoopSimple
from control.songctrl import SongCtrl
from drum.drumfactory import create_drum
from utils.utilalsa import make_sin_sound
from audio.audioinfo import AINFO, correct_sound


def test_1() -> None:
    drum = create_drum('MidiDrum')
    ctrl = SongCtrl(Queue())
    ctrl.set_drum(drum)
    ctrl.get_drum().set_bar_len(100_000)
    ctrl.get_drum().start()

    sound = make_sin_sound(440, 7)
    sound = correct_sound(sound, AINFO.SD_CH, AINFO.SD_TYPE)

    assert ctrl.get_drum().get_bar_len() == 100_000

    loop = LoopSimple()
    loop.record_samples(sound, 0)
    ctrl.idx = len(sound)

    loop.trim_buffer(ctrl)
    Timer(5, ctrl.stop_at_bound, [0]).start()
    loop.play(ctrl)
