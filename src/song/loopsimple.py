import sounddevice as sd

from basic.audioinfo import AudioInfo
from basic.wrapbuffer import WrapBuffer
from control.loopctrl import LoopCtrl


class LoopSimple(WrapBuffer):
    """Loop truncates itself to be multiple of bar length. Bar length is stored in a drum.
    Loop creates drum with proper bar length if drum is empty"""

    def __init__(self, sz: int = AudioInfo().MAX_LEN):
        WrapBuffer.__init__(self, sz)

    def trim_buffer(self, ctrl: LoopCtrl, base_len: int) -> None:
        """trims buffer length to multiple of base_len.
        base_len is length of bar = length of drum """
        self.finalize(ctrl.idx, base_len)
        if not base_len:
            ctrl.drum_create_async(ctrl.idx, dict())

    def play_loop(self, ctrl: LoopCtrl):
        # noinspection PyUnusedLocal
        def callback(in_data, out_data, frame_count, time_info, status):
            out_data[:] = 0
            ctrl.get_drum().play(out_data, ctrl.idx)
            self.play(out_data, ctrl.idx)

            if ctrl.get_is_rec():
                self.record(in_data, ctrl.idx)

            ctrl.idx += frame_count
            if ctrl.idx >= ctrl.get_stop_len():
                ctrl.stop_at_bound(0)

        with sd.Stream(callback=callback):
            ctrl.stop_wait()

        if self.is_empty:
            self.trim_buffer(ctrl, ctrl.get_drum().get_bar_len())
