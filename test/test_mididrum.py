from utils.utilaudio import SD_RATE
from drum.drumfactory import create_drum


def test_1():
    drum = create_drum("MidiDrum")
    drum.set_bar_len(SD_RATE * 2)
    config, bar_len = drum.get_config(), drum.get_bar_len()
    assert bar_len == SD_RATE * 2
    assert "" == config
    drum.start()
    drum.stop()
