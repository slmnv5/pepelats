from utils.utilconfig import SD_RATE
from utils.utilfactory import create_drum


def test_1():
    dr = create_drum("MidiDrum")
    dr.load_config(SD_RATE * 2)
    config, bar_len = dr.get_config(), dr.get_bar_len()
    assert bar_len == SD_RATE * 2
    assert "" == config
    dr.start()
    dr.stop()
