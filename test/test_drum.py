from multiprocessing import Queue
from threading import Timer, Thread
from time import sleep

from control.looper import Looper
from song.loopsimple import LoopSimple
from song.songpart import SongPart
from utils.util_drum import drum_create


def test_1():
    drum = drum_create(100_000, {})
    drum.start()
    part = SongPart()
    part.rec_on()
    Timer(3, part.stop_at_bound, args=[0]).start()
    part.play_loop(drum)  # recording from mic
    sleep(1)
    assert part.get_len() % drum.get_bar_len() == 0
    Timer(3, part.stop_at_bound, args=[0]).start()
    part.play_loop(drum)  # just play


def test_2():
    drum = drum_create(100_000, {})
    drum.start()
    loop = LoopSimple()
    loop.rec_on()
    Timer(3, loop.stop_at_bound, args=[0]).start()
    loop.play_loop(drum)  # recording from mic
    sleep(1)
    drum.randomize()
    assert loop.get_len() % drum.get_bar_len() == 0
    Timer(3, loop.stop_at_bound, args=[0]).start()
    loop.play_loop(drum)  # playing recorded sound + drum


def test_3():
    queue1, queue2 = Queue(), Queue()
    looper = Looper(queue1, queue2)
    Thread(target=looper.client_start, name="process queue", args=[]).start()
    assert looper._drum.get_bar_len() == 0

    looper.drum_create_async(100_000, {"drum_type": "MidiDrum"})
    while not looper._drum.get_bar_len():
        sleep(1)  # wait for another thread to create drum

    drum = looper._drum
    assert drum.get_bar_len() == 100_000
    try:
        drum.set_bar_len(200_000)
        has_exception = False
    except RuntimeError:
        has_exception = True
    assert has_exception
    drum.start()
    drum.randomize()
    drum.play_fill()
    drum.set_param(0.5)
    drum.set_volume(0.5)
    drum.stop()
