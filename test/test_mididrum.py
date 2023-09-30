from utils.utilconfig import SD_RATE
from utils.utilfactory import get_drum
from utils.utilportout import MidiOutWrap


def test_1():
    dr = get_drum("MidiDrum")
    dr.load_drum_config(None, SD_RATE * 2)
    config, bar_len = dr.get_config(), dr.get_bar_len()
    assert bar_len == SD_RATE * 2
    assert "ini" == config[-3:]
    dr.start_drum()
    dr.stop_drum()
