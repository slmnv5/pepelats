from drum._bufferdrum import EuclidPtrnDrum, OldPtrnDrum
from drum._mididrum import MidiDrum
from drum.basedrum import BaseDrum
from drum.loopdrum import LoopDrum
from drum.silentdrum import SilentDrum
from utils.utillog import MYLOG


def create_drum(drum_type: str) -> BaseDrum:
    MYLOG.info(f"Creating drum: {drum_type}")
    if drum_type == "EuclidPtrnDrum":
        return EuclidPtrnDrum()
    elif drum_type == "OldPtrnDrum":
        return OldPtrnDrum()
    elif drum_type == "MidiDrum":
        return MidiDrum()
    elif drum_type == "LoopDrum":
        return LoopDrum()
    elif drum_type == "SilentDrum":
        return SilentDrum()
    else:
        raise RuntimeError(f"Unknown drum type: {drum_type}")
