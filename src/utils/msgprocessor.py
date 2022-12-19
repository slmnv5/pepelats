import traceback
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from typing import Any
from typing import List, Optional

from utils.config import ConfigName
from utils.log import DumbLog


class MsgProcessor:
    def __init__(self, recv_conn: Connection, send_conn: Optional[Connection]):
        self.__recv_conn: Connection = recv_conn
        self.__send_conn: Connection = send_conn

    @staticmethod
    def msg_string(msg: List[Any]) -> List[str]:
        return [str(part) for part in msg]

    def __process_message(self, msg: List[Any]) -> None:
        DumbLog.debug(f"{self.__class__.__name__} got message {MsgProcessor.msg_string(msg)}")
        assert type(msg) == list and len(msg) > 0
        method_name, *params = msg
        # noinspection PyBroadException
        try:
            method = getattr(self, method_name)
            method(*params)
        except Exception:
            DumbLog.error(f"{self.__class__.__name__} in: {method_name} error: {traceback.format_exc()}")

    def process_messages(self):
        while True:
            msg = self.__recv_conn.recv()
            self.__process_message(msg)

    def _send_redraw(self, param) -> None:
        self.__send_conn.send([ConfigName.send_redraw, param])
