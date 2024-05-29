import sounddevice as sd

from audio.wrapbuffer import WrapBuffer
from control.loopctrl import LoopCtrl
from utils.utilconfig import MAX_LEN


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
            ctrl.add_command(["_set_bar_len", ctrl.idx])

    def play_loop(self, ctrl: LoopCtrl):
        drum = ctrl.get_drum()

        # noinspection PyUnusedLocal
        def callback(in_data, out_data, frame_count, time_info, status):
            out_data[:] = 0
            drum.play(out_data, ctrl.idx)
            self.play(out_data, ctrl.idx)

            if ctrl.get_is_rec():
                self.record(in_data, ctrl.idx)

            ctrl.idx += frame_count
            if ctrl.idx >= ctrl.get_stop_len():
                ctrl.stop_at_bound(0)

        with sd.Stream(callback=callback):
            ctrl.get_stop_event().wait()

        self.trim_buffer(ctrl)
