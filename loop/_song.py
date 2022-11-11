import os
import pickle
from abc import abstractmethod
from typing import Dict

from drum import RDRUM
from loop._oneloopctrl import OneLoopCtrl
from loop._songpart import SongPart
from utils import FileFinder, ConfLoader, CollectionOwner, ConfigName
from utils import LOGR
from utils import generate_name


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""
    default_config: Dict = {
        "DRUM_SWING": 0.625,
        "DRUM_VOLUME": 0.5,
        "DRUM_TYPE": "pop",
        "MIXER_IN": 30,
        "MIXER_OUT": 99,
        "SONG_NAME": "first.s"
    }

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
            length, ConfLoader.dic, load_list = pickle.load(f)

        assert type(ConfLoader.dic) == dict
        assert len(load_list) == 4, f"Song must have 4 parts: {self.get_item()}"

        ConfLoader.set_defaults(Song.default_config)
        tmp = ConfLoader.get(ConfigName.drum_type, "pop")
        tmp = RDRUM.first_id(lambda x: self.get_id(x) == tmp, None)
        RDRUM.go_id(tmp)
        RDRUM.prepare_drum(length)
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
        LOGR.info(f"Loaded song file: {full_name}")

    def _save_song(self) -> None:
        length: int = RDRUM.get_length()
        save_list = []
        for k in range(self.item_count):
            x = self.get_id(k)
            save_list.append(x if not x.is_empty else None)

        assert len(save_list) == 4, f"Song must have 4 parts: {self.get_item()}"

        full_name = self._file_finder.get_full_name()
        with open(full_name, 'wb') as f:
            pickle.dump((length, ConfLoader.dic, save_list), f)

        LOGR.info(f"Saved song file {full_name}")

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
