from abc import ABC
from copy import deepcopy
from threading import Event, Thread

from control.loopctrl import LoopCtrl
from song.loopsimple import LoopSimple
from song.song import Song
from song.songpart import SongPart
from utils.utilconfig import ConfigName, SCR_COLS


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
        return part.get_str(pad_str='-', pad_cols=SCR_COLS)

    def _show_parts(self) -> str:
        return self._song.get_str(self.__next_id, '-', pad_cols=SCR_COLS)

    def __play_loop(self) -> None:
        """runs in a thread, play and record current song part"""
        while True:
            self.__play_event.wait()
            self._song.select_idx(self.__next_id)
            part = self._song.get_item()
            self.stop_never()
            self._set_is_rec(part.is_empty or self._start_with_rec)
            if self._start_with_rec:
                part.add_item(LoopSimple(part.get_len()))
            self.idx, self._start_with_rec = 0, False
            self._update_view()
            part.play_loop(self)

    def _part_duplicate(self) -> None:
        part: SongPart = self._song.get_item()
        if part.is_empty:
            return
        for k, x in enumerate(self._song.get_list()):
            if x.is_empty:
                self._song.set_at_idx(k, deepcopy(part))
                self.__next_id = k
                self.stop_at_bound(part.get_len())
                return

    def _part_play(self, part_id: int) -> None:
        """ Play specific part or record new loop of same length if already playing it """
        self._start_with_rec = False
        changed_pid: bool = part_id != self.__next_id  # did next_id change form prev. call
        self.__next_id = part_id

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
                    part.add_item(LoopSimple(part.get_len()))
                    part.clear_undo()
                    self._set_is_rec(True)
        else:  # asked to play another part
            if self.get_is_rec():
                self._set_is_rec(False)
                part.trim_buffer(self)

            self.stop_at_bound(part.get_len())

    def _part_record(self, part_id: int) -> None:
        """ Record new loop of different length. Start with adding empty loop of max. size """
        assert self.__next_id == part_id
        if self._song.get_idx() != part_id:
            self._start_with_rec = True
            return
        part: SongPart = self._song.get_item()
        if part.is_empty:
            return
        if not self.get_is_rec():
            return
        self.idx = self.idx % part.get_max_len(0)
        part.get_item().max_buffer()

    def _part_clear(self, part_id: int) -> None:
        assert self.__next_id == part_id
        selected: int = self._song.get_idx()
        if part_id == selected:
            return  # can not clear active part
        self._song.set_at_idx(part_id, SongPart())
        self.__next_id = selected
        self.stop_never()

    def _part_redo_all(self) -> None:
        if self._song.get_idx() == self.__next_id:
            self._set_is_rec(False)
            part = self._song.get_item()
            while part.redo():
                pass

        # ================= song methods =============================

    def _song_delete(self) -> None:
        self._drum.stop()
        self._song_stop()
        self._song.delete_song()

    def _song_load(self) -> None:
        self._song_stop()
        self._song.load_song()

    def _song_save(self) -> None:
        self._drum.stop()
        self._song_stop()
        self._song.save_song()

    def _song_show_name(self) -> str:
        return self._song.get_complete_name()

    def _song_show_list(self) -> str:
        return self._song.show_list()

    def _song_iterate(self, steps: int) -> None:
        self._song.iterate_song(steps)

    def _song_init(self) -> None:
        self._drum.stop()
        self._song_stop()
        self._song.clear()
        drum_info = self._drum.get_drum_info()
        self.drum_create(0, **drum_info)

    def _drum_type_change(self, drum_type: str) -> None:
        self._drum.stop()
        self._song_stop()
        if drum_type != self._drum.get_class_name():
            bar_len = self._drum.get_bar_len()
            drum_info = {ConfigName.drum_type: drum_type}
            self.drum_create(bar_len, **drum_info)

    def _drum_type_show(self) -> str:
        return "Current drum type: " + self._drum.get_class_name()

    def _song_stop(self, wait: int = 0) -> None:
        self._set_is_rec(False)
        self.__play_event.clear()
        self.__next_id = self._song.get_idx()
        bound = self._song.get_item().get_len() if wait else 0
        self.stop_at_bound(bound)
