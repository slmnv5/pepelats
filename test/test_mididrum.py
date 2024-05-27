from drum.drumfactory import create_drum
from utils.utilaudio import AUDIO


def test_1():
    drum = create_drum("MidiDrum")
    drum.set_bar_len(AUDIO.SD_RATE * 2)
    config, bar_len = drum.get_config(), drum.get_bar_len()
    assert bar_len == AUDIO.SD_RATE * 2
    assert "" == config
    drum.start()
    drum.stop()
