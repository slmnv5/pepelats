import sounddevice

from buffer.loopctrl import LoopCtrl
from buffer.wrapbuffer import WrapBuffer
from utils.utilconfig import MAX_LEN
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class LoopSimple(WrapBuffer):
    """Loop truncates itself to be multiple of bar length. Bar length is stored in a drum.
    Loop creates drum with proper bar length if drum is empty"""

    def __init__(self, sz: int = MAX_LEN):
        WrapBuffer.__init__(self, sz)

    def trim_buffer(self, ctrl: LoopCtrl) -> None:
        """trims length to multiple of bar length"""
        if not self.is_empty:
            return
        drum = ctrl.get_drum()
        bar_len = drum.get_bar_len()
        self.finalize(ctrl.idx, bar_len, 0)
        if not bar_len:
            ctrl.add_command(["_load_drum_config", ctrl.idx])

    def play_buffer(self, ctrl: LoopCtrl):
        drum = ctrl.get_drum()
        play_samples = drum.play_samples(self)  # drum and loop may be the same, avoid double play

        # noinspection PyUnusedLocal
        def callback(in_data, out_data, frame_count, time_info, status):
            out_data[:] = 0
            drum.play_drums(out_data, ctrl.idx)
            if play_samples:
                self.play_samples(out_data, ctrl.idx)

            if ctrl.get_is_rec():
                self.record_samples(in_data, ctrl.idx)

            ctrl.idx += frame_count
            if ctrl.idx >= ctrl.get_stop_len():
                ctrl.stop_at_bound(0)

        with sounddevice.Stream(callback=callback):
            ctrl.get_stop_event().wait()

        self.trim_buffer(ctrl)
