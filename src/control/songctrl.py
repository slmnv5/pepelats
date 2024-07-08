from abc import ABC
from threading import Event, Thread

from control.loopctrl import LoopCtrl
from song.loopsimple import LoopSimple
from song.song import Song
from song.songpart import SongPart
from utils.utilconfig import ConfigName


class SongCtrl(LoopCtrl, ABC):
    """added playback thread and Song.
     Song is collection of song parts with related methods"""

    def __init__(self):
        LoopCtrl.__init__(self)
        self._song: Song = Song(self)
        self.__next_id: int = 0
        self.__play_event: Event = Event()
        self._start_with_rec: bool = False  # if start non-empty loop with recording
        Thread(target=self.__play_loop, name="play_loop", daemon=True).start()

    # ================ song part methods

    def _show_loops(self) -> str:
        part = self._song.get_item()
        return part.loops.get_str()

    def _show_parts(self) -> str:
        return self._song.get_str(self.__next_id)

    def __play_loop(self) -> None:
        """runs in a thread, play and record current song part"""
        while True:
            self.__play_event.wait()
            self._song.select_idx(self.__next_id)
            part = self._song.get_item()
            self.stop_never()
            self._set_is_rec(part.is_empty or self._start_with_rec)
            if self._start_with_rec:
                part.loops.idx_from_item(LoopSimple(part.get_len()))
            self.idx, self._start_with_rec = 0, False
            self._update_view()
            part.play_loop(self)

    def _add_song_part(self) -> None:
        selected: int = self._song.get_idx()
        self.__next_id = self._song.idx_from_item(SongPart())
        self._song.select_idx(selected)

    def _change_song_part(self, chg: int) -> None:
        self.__next_id += chg
        self.__next_id %= self._song.item_count()

    def _play_song_part(self, pid: int) -> None:
        """ Play specific part or record new loop of same length if already playing it """
        self._start_with_rec = False
        changed_pid: bool = pid != self.__next_id  # did next_id change form prev. call
        self.__next_id = pid

        if not self.__play_event.is_set():  # not playing now
            self.__play_event.set()
            return

        selected: int = self._song.get_idx()
        part: SongPart = self._song.get_item()
        if part.is_empty:  # empty part, stop ASAP
            self.stop_at_bound(self._drum.get_bar_len())
            return

        if selected == self.__next_id:  # already playing this part
            if changed_pid:  # just changed our mind, returned back to selected
                self.stop_never()
                return
            else:  # we call with same pid 2nd time
                if self.get_is_rec():
                    self._set_is_rec(False)
                    part.trim_buffer(self)
                else:
                    part.loops.idx_from_item(LoopSimple(part.get_len()))
                    part.clear_undo()
                    self._set_is_rec(True)
        else:  # asked to play another part
            if self.get_is_rec():
                self._set_is_rec(False)
                part.trim_buffer(self)

            self.stop_at_bound(part.get_len())

    def _overdub_song_part(self) -> None:
        """ Record new loop of different length. Start with adding empty loop of max. size """
        if self._song.get_idx() != self.__next_id:
            self._start_with_rec = True
            return
        part: SongPart = self._song.get_item()
        if part.is_empty:
            return
        if not self.get_is_rec():
            return
        self.idx = self.idx % part.get_max_len()
        part.loops.get_item().max_buffer()

    def _delete_song_part(self) -> None:
        selected = self._song.get_idx()
        if self.__next_id == selected:
            return  # can not delete active part
        elif self.__next_id < selected:
            selected -= 1  # selected will be less after deletion

        self._song.select_idx(self.__next_id)
        self._song.delete_selected()
        self._song.select_idx(selected)
        self.__next_id = selected

    def _clear_song_part(self) -> None:
        selected: int = self._song.get_idx()
        if self.__next_id == selected:
            return  # can not clear active part
        self._song.set_at_idx(self.__next_id, SongPart())
        self.__next_id = selected
        self.stop_never()

    def _redo_all(self) -> None:
        if self._song.get_idx() == self.__next_id:
            self._set_is_rec(False)
            part = self._song.get_item()
            while part.redo():
                pass

        # ================= song methods =============================

    def _song_delete(self) -> None:
        self._song_stop()
        self._song.delete_song()

    def _song_load(self) -> None:
        self._song_stop()
        self._song.load_song()

    def _song_save(self) -> None:
        self._song_stop()
        self._song.save_song()

    def _song_name(self) -> str:
        return self._song.get_complete_name()

    def _song_list(self) -> str:
        return self._song.show_songs()

    def _song_iterate(self, steps: int) -> None:
        self._song.iterate_song(steps)

    def _song_init(self) -> None:
        self._drum.stop()
        self._song_stop()
        self._song.clear()
        self._drum = self.drum_create(0)

    def _change_drum(self, drum_type: str) -> None:
        self._drum.stop()
        self._song_stop()
        if drum_type != self._drum.get_class_name():
            bar_len = self._drum.get_bar_len()
            drum_info = {ConfigName.drum_type: drum_type, ConfigName.drum_volume: self._drum.get_volume()}
            self.drum_create(bar_len, **drum_info)

    def _song_stop(self, wait: int = 0) -> None:
        self._set_is_rec(False)
        self.__play_event.clear()
        self.__next_id = self._song.get_idx()
        bound = self._song.get_item().get_len if wait else 0
        self.stop_at_bound(bound)
