import os
from multiprocessing import Queue

from drum.audiodrum import AudioDrum
from drum.basedrum import BaseDrum
from drum.loopdrum import LoopDrum
from drum.mididrum import MidiDrum
from mvc.menuclient import MenuClient
from mvc.pyscreen import PyScreen
from utils.utilconfig import ConfigName, FRAME_BUFFER_ID, find_path
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


def get_screen(recv_q: Queue, send_q: Queue) -> MenuClient:
    try:
        fname = find_path(ConfigName.shared_lib)
        if not os.path.isfile(fname):
            raise RuntimeError(f"Optional lib. {fname} was not found")
        from mvc.ccscreen import CcScreen
        return CcScreen(recv_q, send_q, FRAME_BUFFER_ID)
    except Exception as ex:
        my_log.warning(ex)
        return PyScreen(recv_q)


def create_drum(drum_type: str, **kwargs) -> BaseDrum:
    my_log.info(f"Creating drum: {drum_type}")
    if drum_type == "AudioDrum":
        return AudioDrum()
    elif drum_type == "MidiDrum":
        return MidiDrum()
    elif drum_type == "LoopDrum":
        return LoopDrum(kwargs['SongPart'])
    else:
        my_log.error(f"Unknown drum type: {drum_type}")
        return AudioDrum()
