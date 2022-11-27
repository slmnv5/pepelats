import sys
import traceback
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from typing import Any, List, Optional

from utils.config import ConfigName
from utils.log import LOGGER
from utils.utilother import MenuLoader, RedrawScreen


def msg_string(msg: List[Any]) -> List[str]:
    return [str(part) for part in msg]


class MsgProcessor:
    def __init__(self, recv_conn: Connection, send_conn: Optional[Connection]):
        self.__recv_conn: Connection = recv_conn
        self.__send_conn: Connection = send_conn

    def __process_message(self, msg: List[Any]) -> None:
        LOGGER.debug(f"{self.__class__.__name__} got message {msg_string(msg)}")
        assert type(msg) == list and len(msg) > 0
        method_name, *params = msg
        # noinspection PyBroadException
        try:
            method = getattr(self, method_name)
            method(*params)
        except Exception:
            LOGGER.error(f"{self.__class__.__name__} in: {method_name} error: {traceback.format_exc()}")

    def process_messages(self):
        while True:
            msg = self.__recv_conn.recv()
            self.__process_message(msg)

    def _send_redraw(self, redraw: RedrawScreen) -> None:
        self.__send_conn.send([ConfigName.send_redraw, redraw])


class CmdTranslator(MenuLoader):
    """Translate command with parameters and sends to a connection
    Load config from JSON files in a directory"""

    def __init__(self, send_conn: Connection, load_dir: str, map_name: str, map_id: str):
        MenuLoader.__init__(self, load_dir, map_name, map_id)
        self.__s_conn = send_conn
        self.__menu_loader = MenuLoader(load_dir, map_name, map_id)
        self.__redraw: RedrawScreen = RedrawScreen()
        self.__prepare_redraw()
        self.__s_conn.send([ConfigName.send_redraw, self.__redraw])

    def __prepare_redraw(self):
        self.__redraw.header = ""
        self.__redraw.description = self.__menu_loader.get(ConfigName.description)
        self.__redraw.update = self.__menu_loader.get(ConfigName.update_method)

    def _translate_and_send(self, str_note: str) -> None:
        # map note to command in JSON menu files
        cmd = self.__menu_loader.get(str_note)
        if not cmd:
            return
        # noinspection PyBroadException
        try:
            self.__process_list(cmd)
            LOGGER.info(f"{self.__class__.__name__} sent command: {cmd}")
        except Exception:
            LOGGER.error(f"{self.__class__.__name__} sending command: {cmd} error: {traceback.format_exc()}")

    def __process_list(self, cmd: list) -> None:
        if not cmd:
            return
        head, *tail = cmd
        if isinstance(head, list):
            self.__process_list(head)
            self.__process_list(tail)
        else:
            self.__process_command(cmd)

    def __process_command(self, cmd: list) -> None:
        method_name, *params = cmd
        if method_name == ConfigName.change_map:
            self.__menu_loader.change_map(params[0], params[1])
            self.__prepare_redraw()
        elif method_name == ConfigName.stop_monitor:
            sys.exit(0)
        else:
            self.__s_conn.send(cmd)

        self.__s_conn.send([ConfigName.send_redraw, self.__redraw])


if __name__ == "__main__":
    class FakeConnection(Connection):
        def __init__(self):
            super().__init__(1)

        def send(self, obj: Any) -> None:
            print(f"=======>{str(obj)}<============")


    def test():
        pass


    test()
