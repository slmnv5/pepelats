import os
import pickle
from abc import abstractmethod

from drum import RDRUM, DrumLoader
from loop._oneloopctrl import OneLoopCtrl
from loop._songpart import SongPart
from utils import FileFinder, CollectionOwner, ConfigName
from utils import LOGR
from utils import generate_name


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, first: SongPart):
        CollectionOwner.__init__(self, first)
        self.__part_id: int = 0
        self._file_finder: FileFinder = FileFinder("save_song", True, ".s")

    @property
    def part_id(self) -> int:
        return self.__part_id

    def get_part(self) -> SongPart:
        return self.get_id(self.__part_id)

    def align_ids(self) -> None:
        self.__part_id = self.id

    @abstractmethod
    def _stop_song(self, wait: int = 0) -> None:
        pass

    @abstractmethod
    def _get_control(self) -> OneLoopCtrl:
        pass

    def _load_song(self) -> None:
        self._stop_song()
        full_name = self._file_finder.get_full_name()
        with open(full_name, 'rb') as f:
            length, dic, load_list = pickle.load(f)

        assert type(dic) == dict
        assert len(load_list) == 4, f"Song must have 4 parts: {full_name}"

        tmp1 = dic[ConfigName.drum_type]
        tmp2 = DrumLoader.drum_type
        RDRUM.prepare_drum(length)
        assert tmp1 == tmp2, f"Drum types do not match in saved file: {full_name}, {tmp1}, {tmp2}"

        tmp1 = dic[ConfigName.song_name]
        tmp2 = self._file_finder.get_item()
        assert tmp1 == tmp2, f"Song names do not match in saved file: {full_name}, {tmp1}, {tmp2}"
        ctrl = self._get_control()
        load_list = [x if x is not None else SongPart(ctrl) for x in load_list]

        for part in load_list:
            assert type(part) == SongPart
            part.set_ctrl(ctrl)
            self.append(part)

        while self.item_count > 4:
            self.delete(0, save_backup=False)

        self.go_first()
        self.align_ids()
        LOGR.info(f"Loaded song file: {full_name}, saved: {dic}")

    def _save_song(self) -> None:
        full_name = self._file_finder.get_full_name()
        length: int = RDRUM.get_length()
        save_list = list()
        for k in range(self.item_count):
            x = self.get_id(k)
            save_list.append(x if not x.is_empty else None)

        dic = dict()
        dic[ConfigName.song_name] = self._file_finder.get_item()
        dic[ConfigName.drum_type] = DrumLoader.drum_type
        dic[ConfigName.drum_volume] = DrumLoader.volume
        dic[ConfigName.drum_swing] = DrumLoader.swing

        assert len(save_list) == 4, f"Song must have 4 parts: {full_name}"

        with open(full_name, 'wb') as f:
            pickle.dump((length, dic, save_list), f)

        LOGR.info(f"Saved song file {full_name}, saved: {dic}")

    def _save_new_song(self):
        tmp = self.__new_song_name()
        self._file_finder.append(tmp)
        self._file_finder.go_last()
        self._save_song()

    def _delete_song(self) -> None:
        self._stop_song()
        path = self._file_finder.get_full_name()
        if os.path.isfile(path):
            os.remove(path)
        self._file_finder.delete(self._file_finder.id, save_backup=False)
        self._file_finder.iterate(True)
        self._stop_song()

    def __new_song_name(self) -> str:
        return generate_name() + self._file_finder.get_end_with()
