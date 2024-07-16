from multiprocessing import Queue
from threading import Thread

from mvc.basescreen import BaseScreen
from serv.webserver import WebHelper
from utils.utilother import DrawInfo


class WebScreen(BaseScreen, WebHelper):
    def __init__(self, q: Queue):
        BaseScreen.__init__(self, q)
        WebHelper.__init__(self)
        Thread(target=self.serve_forever(), name="updater", daemon=True).start()

    def _client_stop(self) -> None:
        super()._client_stop()
        self.shutdown()

    def _menu_client_redraw(self, di: DrawInfo) -> None:
        self.handler_class.di = di
        self.handler_class.has_update.set()


if __name__ == "__main__":
    WebScreen(Queue())
