import sounddevice

from buffer.loopctrl import LoopCtrl
from buffer.wrapbuffer import WrapBuffer
from utils.utilconfig import MAX_LEN
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class LoopSimple(WrapBuffer):
    """Loop truncate itself to be multiple of bar length.
    Or init bar length if it is empty"""

    def __init__(self, length: int = MAX_LEN):
        WrapBuffer.__init__(self, length)

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
        play_drum = drum.get_id() != id(self)  # drum may play twice

        # noinspection PyUnusedLocal
        def callback(in_data, out_data, frame_count, time_info, status):
            out_data[:] = 0
            if play_drum:
                drum.play_drums(out_data, ctrl.idx)
            self.play_samples(out_data, ctrl.idx)

            if ctrl.get_is_rec():
                self._record_samples(in_data, ctrl.idx)

            ctrl.idx += frame_count
            if ctrl.idx >= ctrl.get_stop_len():
                ctrl.stop_at_bound(0)

        with sounddevice.Stream(callback=callback):
            ctrl.get_stop_event().wait()

        self.trim_buffer(ctrl)
