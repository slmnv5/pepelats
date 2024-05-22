from multiprocessing import Queue
from threading import Timer

from buffer.loopctrl import LoopCtrl
from song.songpart import SongPart
from utils.utilfactory import create_drum


def test_1():
    queue = Queue()
    drum = create_drum("PatternDrum")
    c1 = LoopCtrl(queue, drum)
    c1._set_is_rec(True)
    Timer(3, c1.stop_at_bound, args=[0]).start()
    l1 = SongPart()
    l1.play_buffer(c1)
    c1.stop_never()
    Timer(5, c1.stop_at_bound, args=[0]).start()
    l1.play_buffer(c1)
