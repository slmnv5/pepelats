import os
from multiprocessing import Queue
from time import sleep

from control._songctrl import SongCtrl
from screen.confighandler import run_web_config_server
from utils.util_config import LOCAL_IP, ram_usage_pct, cpu_usage_pct, get_selected_branch, get_branch_update, \
    select_next_branch, load_ini_section, update_ini_section
from utils.util_drum import drum_create
from utils.util_log import MY_LOG
from utils.util_name import AppName


class Looper(SongCtrl):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_q: Queue, send_q: Queue):
        SongCtrl.__init__(self, recv_q)
        self.__queue = send_q
        self._description: str = ""
        self._content: str = ""
        self._drum_create(0, dict())

    def _client_stop(self) -> None:
        self._client_enqueue([AppName.client_stop])
        super()._client_stop()
        self._song_stop()

    def drum_create_async(self, bar_len: int, drum_info: dict) -> None:
        self._client_enqueue(['_drum_create', bar_len, drum_info])

    def _drum_create(self, bar_len: int, drum_info: dict) -> None:
        self._drum = drum_create(bar_len, drum_info)
        self._drum.start()

    def _update_view(self) -> None:
        self._client_enqueue([AppName.client_redraw, dict()])

    def _client_redraw(self, dic: dict) -> None:
        dic[AppName.header] = f"{self._drum}"

        if AppName.description in dic:
            self._description = dic[AppName.description]
        else:
            dic[AppName.description] = self._description

        if AppName.content in dic:
            self._content = dic[AppName.content]

        # noinspection PyBroadException
        try:
            method = getattr(self, self._content)
            dic[AppName.content] = method()
        except Exception as ex:
            dic[AppName.content] = ""
            MY_LOG.exception(ex)

        part = self._song.parts.get_item()
        dic["len"] = part.get_len()
        dic["max_loop_len"] = part.get_base_len(self._drum)
        dic["idx"] = part.get_index()
        dic["is_rec"] = part.is_rec()
        self.__queue.put([AppName.client_redraw, dic])

    # other methods

    @staticmethod
    def _info_show_0() -> str:
        return (f"app. ver. {get_selected_branch()}\n{get_branch_update()}\n"
                f"use of RAM% {ram_usage_pct()} CPU% {cpu_usage_pct()}")

    def _info_show_1(self) -> str:
        scr_type: int = load_ini_section("SCREEN", True).get(AppName.screen_type, 0)
        dr_type: str = self._drum.get_class_name()
        return f"drum: {dr_type}\nscreen: {scr_type} (0-lcd 1-web)\nlocal IP: {LOCAL_IP}"

    @staticmethod
    def _branch_change() -> None:
        select_next_branch()

    @staticmethod
    def _screen_type_change() -> None:
        if not LOCAL_IP:
            MY_LOG.error(f"Can not change screen type without WiFi connection")
            return
        dic = load_ini_section("SCREEN", True)
        scr_type: int = dic.get(AppName.screen_type, 0)
        scr_type = (scr_type + 1) % 2
        dic[AppName.screen_type] = str(scr_type)
        update_ini_section("SCREEN", dic)

    @staticmethod
    def _looper_update() -> None:
        os.system("git reset --hard; git pull")
        sleep(5)

    def _web_config(self) -> None:
        self._song_stop()
        run_web_config_server()
        self._client_clear_queue()

    #  parts methods

    def _part_undo(self) -> None:
        part = self._song.parts.get_item()
        is_rec = part.is_rec()
        part.rec_off()
        if not is_rec:
            part.undo()

    def _part_redo(self) -> None:
        part = self._song.parts.get_item()
        part.rec_off()
        part.redo()

    # one part methods

    def _loop_iterate(self, steps: int) -> None:
        self._song.parts.get_item().loops.iterate(steps)

    def _loop_edit(self, action: str) -> None:
        part = self._song.parts.get_item()
        loop = part.loops.get_item()
        if action == "silent":
            loop.set_silent(not loop.is_silent())
        elif action == "reverse":
            loop.flip_reverse()
        elif action == "move" and part != loop:
            deleted = part.loops.delete_item()
            if deleted:
                part.loops.add_item(deleted)
        elif action == "delete" and part != loop:
            part.loops.delete_item()


if __name__ == "__main__":
    select_next_branch()
