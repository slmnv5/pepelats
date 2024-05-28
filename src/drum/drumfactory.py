from drum._bufferdrum import BufferDrum
from drum.basedrum import BaseDrum
from drum._eucliddrum import EuclidPtrnLoader
from drum.loopdrum import LoopDrum
from drum._mididrum import MidiDrum
from drum._patterndrum import OldPtrnLoader
from drum.silentdrum import SilentDrum
from utils.utillog import MYLOG


def create_drum(drum_type: str) -> BaseDrum:
    MYLOG.info(f"Creating drum: {drum_type}")
    if drum_type == "EuclidDrum":
        return BufferDrum(EuclidPtrnLoader())
    elif drum_type == "PatternDrum":
        return BufferDrum(OldPtrnLoader())
    elif drum_type == "MidiDrum":
        return MidiDrum()
    elif drum_type == "LoopDrum":
        return LoopDrum()
    elif drum_type == "SilentDrum":
        return SilentDrum()
    else:
        raise RuntimeError(f"Unknown drum type: {drum_type}")
