from multiprocessing import Queue
from threading import Timer, Thread
from time import sleep

from control.looper import Looper
from drum.drumfactory import create_drum
from song.loopsimple import LoopSimple
from song.songpart import SongPart
from utils.utilconfig import ConfigName
from utils.utilconfig import SD_RATE


def test_1():
    queue1, queue2 = Queue(), Queue()
    looper = Looper(queue1, queue2, ConfigName.StyleDrum)
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
    looper = Looper(queue1, queue2, ConfigName.EuclidDrum)
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
    drum = create_drum(100_000, drum_type="MidiDrum")
    drum.set_bar_len(SD_RATE * 2)
    bar_len = drum.get_bar_len()
    assert bar_len == SD_RATE * 2
    drum.start()
    drum.stop()
