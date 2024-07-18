import os
import subprocess
from configparser import ConfigParser, ParsingError
from http.server import BaseHTTPRequestHandler
from typing import Callable

from utils.utillog import MyLog
from utils.utilother import split_to_dict
from utils.utilweb import FILE_FORM_PAGE, CONFIG_PAGE, RESET_PATH, EXIT_PATH, EDIT_PATH, SHOW_PATH


class ConfigHandler(BaseHTTPRequestHandler):
    get_updates: Callable[[], str] = None

    def _write_to_file(self) -> bool:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()  # <--- Gets the data
        type_list = self.headers.get('Content-Type', '').split("boundary=")

        if len(type_list) != 2:
            return False

        bound = "--" + type_list[1]  # separates each data item in post_data: k=v
        mark1 = 'Content-Disposition: form-data; name='  # placed before k=
        mark2 = '\r\n\r\n'  # placed after k=
        data_dict = split_to_dict(post_data, bound, mark1, mark2, '\'\" \r\n\t', ' \r\n\t')

        if "file_name" not in data_dict or "file_data" not in data_dict:
            return False

        fname = data_dict["file_name"]
        if not os.path.isfile(fname) or os.path.islink(fname):
            return False

        if fname[-4:].lower() == ".ini":
            cfg = ConfigParser()
            try:
                cfg.read_string(data_dict["file_data"])
            except ParsingError as ex:
                self.wfile.write(f"Parsing form data failed: {ex}".encode())
                return False

        with open(fname, 'w') as f:
            f.write(data_dict["file_data"])
        return True

    def _send_redirect(self) -> None:
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/')  # This will navigate to the original page
        self.end_headers()

    def _send_file(self, fname: str, read_only: bool) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if os.path.islink(fname):
            self.wfile.write(f"File is link: {fname}".encode())
        elif not os.path.isfile(fname):
            self.wfile.write(f"File not found: {fname}".encode())
        else:
            with open(fname, 'r') as f:
                data = f.read()

        disabled = "disabled" if read_only else ""
        html = FILE_FORM_PAGE.format(disabled=disabled, file_name=fname, file_data=data)
        self.wfile.write(html.encode())

    def _send_page(self, page: bytes) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(page)

    # noinspection PyPep8Naming
    def do_GET(self):
        MyLog().info(f"path:{self.path}\nheaders:{self.headers}")
        if self.path == "/":
            self._send_page(CONFIG_PAGE)
        elif self.path == RESET_PATH:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            result = subprocess.run(['git', 'reset', '--hard'], stdout=subprocess.PIPE)
            self.wfile.write(result.stdout)
        elif self.path == EXIT_PATH:
            raise KeyboardInterrupt()
        elif self.path.startswith(EDIT_PATH):
            fname = self.path[len(EDIT_PATH):]
            self._send_file(fname, False)
        elif self.path.startswith(SHOW_PATH):
            fname = self.path[len(SHOW_PATH):]
            self._send_file(fname, True)
        elif self.path == "/favicon.ico":
            with open("./favicon.ico", 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(400, "Not found", f"Not found: {self.path}")

    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path != "/save_file":
            self._send_redirect()
        else:
            if self._write_to_file():
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("Successfully updated file".encode())
            else:
                self.send_error(400, "Bad Request", "Parsing form data failed")
