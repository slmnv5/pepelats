from drum.drumfactory import create_drum
from utils.utilconfig import SD_RATE


def test_1():
    drum = create_drum("MidiDrum")
    drum.set_bar_len(SD_RATE * 2)
    config, bar_len = drum.get_config(), drum.get_bar_len()
    assert bar_len == SD_RATE * 2
    assert "Midi" == config
    drum.start()
    drum.stop()
