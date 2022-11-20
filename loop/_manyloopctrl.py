from threading import Thread, Event

from drum import FakeDrum
from loop._loopsimple import LoopSimple
from loop._oneloopctrl import OneLoopCtrl
from loop._song import Song
from loop._songpart import SongPart
from utils import MAX_LEN


class ManyLoopCtrl(OneLoopCtrl, Song):
    """added playback thread and Song.
     Song is collection of song parts with related methods"""

    def __init__(self, drum: FakeDrum):
        self._play_event: Event = Event()
        OneLoopCtrl.__init__(self, drum)
        Song.__init__(self, SongPart(self))
        Thread(target=self.__playback, name="playback_thread", daemon=True).start()
        self._file_finder.go_id(0)
        self._init_song()

    def get_play_event(self) -> Event:
        return self._play_event

    def _redraw(self) -> None:
        pass

    def _get_control(self) -> OneLoopCtrl:
        return self

    def _init_song(self) -> None:
        self._stop_song()
        Song.__init__(self, SongPart(self))
        while self.item_count < 4:
            self.append(SongPart(self))

        ff = self._file_finder
        ff.set_fixed("")

        self.set_fixed(self.get_id(0))
        self.align_ids()
        self.get_drum().clear_drum()

    def __playback(self) -> None:
        """runs in a thread, play and record current song part"""
        while True:
            self._play_event.wait()
            self.align_ids()

            part = self.get_part()
            self.get_stop_event().clear()
            self._stop_never()
            self.idx = 0
            self._is_rec = part.is_empty
            part.play_buffer()

    def _stop_song(self, wait: int = 0) -> None:
        self._is_rec = False
        self._play_event.clear()
        if not wait:
            self.stop_at_bound(0)
        else:
            self.stop_at_bound(self.get_part().length)

    def _record_part(self):
        if self.id == self.fixed_id and self._is_rec:
            part = self.get_part()
            loop = part.get_item()
            if not loop.is_empty:
                loop.resize_buff(MAX_LEN)

    def _play_part_id(self, fixed_id: int) -> None:
        if not self._play_event.is_set():
            self.go_id(fixed_id)
            self._play_event.set()
            return

        if fixed_id != self.id:
            self.go_id(fixed_id)
            self._stop_never()
            if fixed_id == self.fixed_id:
                return

        part = self.get_part()
        loop = part.get_item()
        if part.id > 0 and self._is_rec and loop.is_empty:
            loop.finalize(self.idx, part.length)

        if self.id == self.fixed_id:
            if self._is_rec:
                self._is_rec = False
            else:
                part.append(LoopSimple(self, part.length))
                part.go_id(part.item_count - 1)
                self._is_rec = True

        self.__stop_quantized()

    def __stop_quantized(self) -> None:
        """the method for quantized playback and recording,
        has logic when to stop playback"""
        part = self.get_part()
        if part.is_empty:
            if not self.get_drum().get_length():
                self.stop_at_bound(0)
            else:
                self.stop_at_bound(self.get_drum().get_length())
        else:
            if self.id != self.fixed_id:
                if self.is_stop_len_set():
                    self.stop_at_bound(self.get_drum().get_length())
                else:
                    self.stop_at_bound(part.length)
                    self.get_drum().play_break_later(part.length, self.idx)
            else:
                self._stop_never()

    # ====== drum related

    def _change_drum_volume(self, change_factor: float) -> None:
        self.get_drum().change_volume(change_factor)

    def _change_drum_swing(self, change_steps: int) -> None:
        self.get_drum().change_swing(change_steps)

    def _change_drum(self) -> None:
        self.get_drum().play_break_now()

    def _change_drum_intensity(self, change_by: int) -> None:
        self.get_drum().change_intensity(change_by)

    def _show_drum_param(self) -> str:
        return f"Drum parameters:\nvolume(0-100):{self.get_drum().get_volume():.0F}\n" \
               f"swing(0.5-0.75):{self.get_drum().get_swing():.2F}"


if __name__ == "__main__":
    def test(use_midi: bool):
        from loop._loopsimple import LoopSimple
        from loop._oneloopctrl import OneLoopCtrl
        from threading import Timer
        from drum import RealDrum, MidiDrum
        import time

        drum = MidiDrum() if use_midi else RealDrum()

        # drum.prepare_drum(100_000)
        # while not drum.get_length():
        #    time.sleep(0.1)

        duration: float = 7.5

        print("======== start record =============")
        ctrl = ManyLoopCtrl(drum)
        ctrl.get_play_event().set()
        Timer(duration, ctrl.stop_at_bound, [0]).start()
        time.sleep(duration)

        print("======== start palay =============")
        ctrl.get_play_event().set()
        Timer(duration, ctrl.stop_at_bound, [0]).start()
        time.sleep(duration)


    test(True)

    # test(False)
