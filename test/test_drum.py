from multiprocessing import Queue
from threading import Timer, Thread
from time import sleep

from control.looper import Looper
from song.loopsimple import LoopSimple
from song.songpart import SongPart
from utils.utilconfig import ConfigName


def test_1():
    queue1, queue2 = Queue(), Queue()
    looper = Looper(queue1, queue2)
    t = Thread(target=looper.menu_client_start, name="process queue", args=[])
    t.start()  # start processing message queue

    part = SongPart()
    print("Looper", looper)
    print("Part", part)

    assert looper.get_drum().get_bar_len() == 0
    looper._set_is_rec(True)
    Timer(3, looper.stop_at_bound, args=[0]).start()
    part.play_loop(looper)  # recording from mic
    while not looper.get_drum().get_bar_len():
        sleep(1)  # wait for another thread to create drum

    assert looper.get_drum().get_bar_len()
    looper._drum_randomize()
    looper.stop_never()
    Timer(3, looper.stop_at_bound, args=[0]).start()
    part.play_loop(looper)  # playing recorded sound + drum
    queue1.put([ConfigName.menu_client_stop])
    assert looper.get_drum().get_bar_len() == part.get_len()


def test_2():
    queue1, queue2 = Queue(), Queue()
    looper = Looper(queue1, queue2)
    t = Thread(target=looper.menu_client_start, name="process queue", args=[])
    t.start()  # start processing message queue

    loop = LoopSimple()
    print("SongCtrl", looper)
    print("Loop", loop)

    assert looper.get_drum().get_bar_len() == 0
    looper._set_is_rec(True)
    Timer(3, looper.stop_at_bound, args=[0]).start()
    loop.play_loop(looper)  # recording from mic
    while not looper.get_drum().get_bar_len():
        sleep(1)  # wait for another thread to create drum

    looper._drum_randomize()
    assert looper.get_drum().get_bar_len()
    looper.stop_never()
    Timer(3, looper.stop_at_bound, args=[0]).start()
    loop.play_loop(looper)  # playing recorded sound + drum
    queue1.put([ConfigName.menu_client_stop])
    assert looper.get_drum().get_bar_len() == loop.get_len()


def test_3():
    queue1, queue2 = Queue(), Queue()
    looper = Looper(queue1, queue2)
    looper.drum_create(100_000, drum_type="MidiDrum")
    drum = looper.get_drum()
    bar_len = drum.get_bar_len()
    assert bar_len == 100_000
    try:
        drum.set_bar_len(200_000)
        has_exception = False
    except AssertionError:
        has_exception = True
    assert has_exception
    drum.start()
    drum.randomize()
    drum.play_fill(100_000)
    drum.set_par(0.5)
    drum.set_volume(0.5)
    drum.stop()
