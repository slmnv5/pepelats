from threading import Thread, Event

from drum import RDRUM
from loop._loopsimple import LoopWithDrum
from loop._oneloopctrl import OneLoopCtrl
from loop._song import Song
from loop._songpart import SongPart
from utils import MAX_LEN


class ManyLoopCtrl(OneLoopCtrl, Song):
    """added playback thread, MsgProcessor and Song.
     Song is collection of song parts with related methods"""

    def __init__(self):
        self._go_play: Event = Event()
        OneLoopCtrl.__init__(self)
        Song.__init__(self, SongPart(self))
        Thread(target=self.__playback, name="playback_thread", daemon=True).start()
        self._file_finder.go_first()
        self._init_song()

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
        ff.set_fixed(ff.get_empty_name())
        assert ff.get_item() == ff.get_empty_name()

        self.set_fixed(self.get_first())
        self.align_ids()
        RDRUM.clear_drum()

    def __playback(self) -> None:
        """runs in a thread, play and record current song part"""
        while True:
            self._go_play.wait()
            self.align_ids()

            part = self.get_part()
            self.get_stop_event().clear()
            self._stop_never()
            self.idx = 0
            self._is_rec = part.is_empty
            part.play_buffer()

    def _stop_song(self, wait: int = 0) -> None:
        self._is_rec = False
        self._go_play.clear()
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
        if not self._go_play.is_set():
            self.go_id(fixed_id)
            self._go_play.set()
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
                part.append(LoopWithDrum(self, part.length))
                part.go_last()
                self._is_rec = True

        self.__stop_quantized()

    def __stop_quantized(self) -> None:
        """the method for quantized playback and recording,
        has logic when to stop playback"""
        part = self.get_part()
        if part.is_empty:
            if not RDRUM.get_length():
                self.stop_at_bound(0)
            else:
                self.stop_at_bound(RDRUM.get_length())
        else:
            if self.id != self.fixed_id:
                if self.is_stop_len_set():
                    self.stop_at_bound(RDRUM.get_length())
                else:
                    self.stop_at_bound(part.length)
                    RDRUM.play_break_later(part.length, self.idx)
            else:
                self._stop_never()

    # ====== drum related

    @staticmethod
    def _change_drum_volume(change_by: int) -> None:
        RDRUM.change_volume(change_by)

    @staticmethod
    def _change_drum_swing(change_by: int) -> None:
        RDRUM.change_swing(change_by)

    @staticmethod
    def _change_drum() -> None:
        RDRUM.play_break_now()

    @staticmethod
    def _change_drum_intensity(change_by: int) -> None:
        RDRUM.change_intensity(change_by)

    @staticmethod
    def _show_drum_param() -> str:
        return f"Drum parameters:\nvolume(0.0-1.0):{RDRUM.get_volume():.2F}\n" \
               f"swing(0.5-0.75):{RDRUM.get_swing():.2F}"


if __name__ == "__main__":
    pass
