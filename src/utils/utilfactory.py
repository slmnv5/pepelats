from drum.basedrum import BaseDrum
from drum.eucliddrum import EuclidDrum
from drum.loopdrum import LoopDrum
from drum.mididrum import MidiDrum
from drum.patterndrum import PatternDrum
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


def create_drum(drum_type: str, **kwargs) -> BaseDrum:
    my_log.info(f"Creating drum: {drum_type}")
    if drum_type == "EuclidDrum":
        return EuclidDrum()
    elif drum_type == "PatternDrum":
        return PatternDrum()
    elif drum_type == "MidiDrum":
        return MidiDrum()
    elif drum_type == "LoopDrum":
        return LoopDrum(kwargs['SongPart'])
    else:
        my_log.error(f"Unknown drum type: {drum_type}")
        return PatternDrum()
