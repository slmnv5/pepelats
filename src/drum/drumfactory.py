from drum.basedrum import BaseDrum
from drum.eucliddrum import EuclidDrum
from drum.loopdrum import LoopDrum
from drum.mididrum import MidiDrum
from drum.patterndrum import PatternDrum
from drum.silentdrum import SilentDrum
from utils.utillog import MyLog

my_log = MyLog()


def create_drum(drum_type: str) -> BaseDrum:
    my_log.info(f"Creating drum: {drum_type}")
    if drum_type == "EuclidDrum":
        return EuclidDrum()
    elif drum_type == "PatternDrum":
        return PatternDrum()
    elif drum_type == "MidiDrum":
        return MidiDrum()
    elif drum_type == "LoopDrum":
        return LoopDrum()
    elif drum_type == "SilentDrum":
        return SilentDrum()
    else:
        raise RuntimeError(f"Unknown drum type: {drum_type}")
