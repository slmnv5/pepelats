from abc import ABC
from multiprocessing import Queue
from threading import Event, Thread

from control.loopctrl import LoopCtrl
from drum.loopdrum import LoopDrum
from screen.menuclient import MenuClient
from song.loopsimple import LoopSimple
from song.song import Song, load_song_drum, save_song_drum
from song.songpart import SongPart
from utils.util_name import AppName
from utils.util_screen import SCR_ROWS


class SongCtrl(MenuClient, LoopCtrl, ABC):
    """added playback thread and Song.
     Song is collection of song parts with related methods"""

    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        LoopCtrl.__init__(self)
        self._song: Song = Song()
        self.__next_idx: int = 0
        self.__prev_idx: int = -1
        self.__play_event: Event = Event()
        self.__rec_start: bool = False  # record on at start
        Thread(target=self.__run, name="run", daemon=True).start()

    def __run(self) -> None:
        """runs in a thread, play and record current song part"""
        while self._alive:
            self.__play_event.wait()
            part = self._song.parts.select_idx(self.__next_idx)
            if self.__rec_start:
                part.clear_undo()
                part.rec_on()
            self.__rec_start = False
            self._update_view()
            part.play_loop(self._drum)
            if not self._drum.get_bar_len():
                dic = {AppName.song_part: self._song.parts.get_first()}
                self.drum_create_async(part.get_len(), dic)

    # song part methods

    def _show_loops(self) -> str:
        part = self._song.parts.get_item()
        return part.loops.get_str(SCR_ROWS - 5)

    def _show_parts(self) -> str:
        return self._song.parts.get_str(SCR_ROWS - 5, self.__next_idx)

    def _part_change(self, part_id: int) -> None:
        """ set next part and set stop time for current part """
        self.__next_idx, self.__prev_idx = part_id, self.__next_idx

        if not self.__play_event.is_set():  # not playing now
            self.__play_event.set()
            return

        part = self._song.parts.get_item()
        if part.is_empty():  # empty part, stop ASAP
            part.stop_at_bound(self._drum.get_bar_len())
            self.__prev_idx = -1
            return

        if self._song.parts.get_idx() == self.__next_idx:  # already playing this part
            part.stop_never()
            return

        part.stop_at_bound(part.get_len())  # stop when current part ends and switch to self.__next_id

    def _part_record(self) -> None:
        """ self.__next_idx has been set already. Record or play logic """
        selected: int = self._song.parts.get_idx()
        if self.__next_idx != selected:
            return  # self.__next_idx still not here, keep playing
        elif self.__prev_idx != selected:
            return  # first time at selected, just play
        else:
            pass  # need to record or stop record

        part = self._song.parts.get_item()
        if part.is_empty():  # empty part is always recording
            return

        if part.is_rec():
            part.rec_off()
            loop = part.loops.get_item()
            if loop.is_empty():
                part.trim_buffer(part.get_index(), part.get_base_len(self._drum))
        else:
            part.clear_undo()  # when new loop recorded old undone loops always deleted
            part.loops.add_item(LoopSimple(part.get_len()))
            part.rec_on()

    def _part_record_ext(self) -> None:
        """ self.__next_idx has been set already.
        Record loop of different length, or start next part with reccording - double tap """
        self.__rec_start = False
        part: SongPart = self._song.parts.get_item()
        if self._song.parts.get_idx() != self.__next_idx:
            self.__rec_start = True  # another part will start with recording
        elif not (part.is_empty() or part.is_rec()):
            part.clear_undo()
            part.loops.add_item(LoopSimple())
            part.rec_on()

    def _part_clear(self) -> None:
        """ self.__next_idx has been set already. Clear next part """
        selected: int = self._song.parts.get_idx()
        if self.__next_idx == selected:
            return  # can not clear active part
        if isinstance(self._drum, LoopDrum) and self.__next_idx == 0:
            return  # part zero used by loop drum
        self._song.parts.select_idx(self.__next_idx).clear()
        self.__next_idx, self.__prev_idx = selected, -1
        self._song.parts.select_idx(selected).stop_never()

    def _part_redo_all(self) -> None:
        part = self._song.parts.get_item()
        part.rec_off()
        while part.redo():
            pass

    # song methods

    def _song_delete(self) -> None:
        self._song_stop()
        self._song.delete_song()

    def _song_load(self) -> None:
        self._song_stop()
        self._song, self._drum = load_song_drum()

    def _song_save(self) -> None:
        self._song_stop()
        save_song_drum(self._song, self._drum)

    def _song_show_name(self) -> str:
        return self._song.get_complete_name(self._drum)

    def _song_show_list(self) -> str:
        return self._song.show_list()

    def _song_iterate(self, steps: int) -> None:
        self._song.iterate_song(steps)

    def _song_init(self) -> None:
        self._song_stop()
        self._song.clear()
        drum_info = self._drum.get_drum_info()
        self.drum_create_async(0, drum_info)

    def _drum_type_change(self, drum_type: str) -> None:
        self._song_stop()
        if drum_type != self._drum.get_class_name():
            bar_len = self._drum.get_bar_len()
            drum_info = {AppName.drum_type: drum_type}
            self.drum_create_async(bar_len, drum_info)

    def _song_stop(self, wait: int = 0) -> None:
        self._drum.stop()
        part = self._song.parts.get_item()
        part.rec_off()
        self.__play_event.clear()
        self.__next_idx = self._song.parts.get_idx()
        bound = part.get_base_len(self._drum) if wait else 0
        part.stop_at_bound(bound)
