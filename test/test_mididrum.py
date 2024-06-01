from drum.drumfactory import DrumFactory
from utils.utilconfig import SD_RATE


def test_1():
    drum = DrumFactory.create_drum(100_000, drum_type="MidiDrum")
    drum.set_bar_len(SD_RATE * 2)
    bar_len = drum.get_bar_len()
    assert bar_len == SD_RATE * 2
    drum.start()
    drum.stop()
