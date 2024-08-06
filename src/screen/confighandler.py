import os
import subprocess
from configparser import ConfigParser
from http.server import BaseHTTPRequestHandler, HTTPServer

from utils.util_config import LOCAL_IP, LOCAL_PORT
from utils.util_log import MY_LOG
from utils.util_other import split_to_dict
from utils.util_web import EDIT_PATH, load_file, CONFIG_PATH, CONFIG_PAGE_B, load_bin_file


class ConfigHandler(BaseHTTPRequestHandler):

    def _send_any_file(self, fname: str, content_type: str, is_binary: bool = False) -> None:
        fname = "html" + fname.strip()
        try:
            self.send_hdr(arg_dic={'Content-type': content_type})
            if is_binary:
                self.wfile.write(load_bin_file(fname))
            else:
                self.wfile.write(load_file(fname).encode())
        except Exception as ex:
            MY_LOG.exception(ex)
            MY_LOG.error(f"Error sending file: {fname} / {content_type}")

    def _process_get(self) -> str | None:
        """ returns self.path if not processed, else None """
        if self.path == "/":
            self._send_any_file("/main_page.html", "text/html")
        elif self.path == CONFIG_PATH:
            self.send_hdr()
            self.wfile.write(CONFIG_PAGE_B)
        elif self.path.startswith(EDIT_PATH):
            fname = self.path[len(EDIT_PATH):]
            self._send_file_form(fname)
        elif self.path.endswith(".html"):
            self._send_any_file(self.path, "text/html")
        elif self.path.endswith(".ico"):
            self._send_any_file(self.path, "application/octet-stream", True)
        elif self.path.endswith(".css"):
            self._send_any_file(self.path, 'text/css')
        elif self.path.endswith(".js"):
            self._send_any_file(self.path, "text/javascript")
        else:
            return self.path  # not my path

    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path == "/save_file":
            self._write_to_file()
        elif self.path == "/run_command":
            self._run_command()
        else:
            return self.path  # not known path, keep it for subclass

    def send_hdr(self, status: int = 200, arg_dic=None) -> None:
        d: dict[str, str] = {'Content-type': 'text/html'}
        if arg_dic is not None:
            d.update(arg_dic)
        self.send_response(status)
        for k, v in d.items():
            assert isinstance(k, str) and isinstance(v, str), f"must be strings: k={k}, v={v}"
            self.send_header(k, v)
        self.end_headers()

    def _get_data_dict(self) -> dict[str, str]:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()  # <--- Gets the data
        type_list = self.headers.get('Content-Type', "").split("boundary=")
        if len(type_list) != 2:
            return dict()
        bound = "--" + type_list[1]  # separates each data item in post_data: k=v
        mark1 = 'Content-Disposition: form-data; name='  # placed before k=
        mark2 = '\r\n\r\n'  # placed after k=
        return split_to_dict(post_data, bound, mark1, mark2, '\'\" \r\n\t', ' \r\n\t')

    def _run_command(self) -> None:
        try:
            data_dict = self._get_data_dict()
            cmd_lst: list[str] = data_dict["command_line"].split()
            cmd_out = subprocess.run(cmd_lst, stdout=subprocess.PIPE).stdout.decode()
            self.send_hdr()
            html = load_file("html/command_output.html")
            html.format(cmd_out)
            self.wfile.write(html.format(cmd_out).encode())
        except Exception as ex:
            msg = f"Could not run command, error: {ex}"
            MY_LOG.error(msg)
            self.send_hdr()
            self.wfile.write(msg.encode())

    def _write_to_file(self) -> None:
        try:
            data_dict = self._get_data_dict()
            fname: str = data_dict["file_name"]
            file_data: str = data_dict["file_data"]

            if not os.path.isfile(fname) or os.path.islink(fname):
                raise RuntimeError(f"File not found: {fname}")

            if fname[-4:].lower() == ".ini":  # check INI parsing
                ConfigParser().read_string(file_data)

            with open(fname, 'wb') as f:
                f.write(file_data.encode())

            self.send_hdr()
            self.wfile.write(f"Saved file: {fname}".encode())
        except Exception as ex:
            msg = f"Could not save file, error: {ex}"
            MY_LOG.error(msg)
            self.send_hdr()
            self.wfile.write(msg.encode())

    def _send_file_form(self, fname: str) -> None:
        if os.path.islink(fname) or not os.path.isfile(fname):
            self.send_error(400, "Bad Request")
        else:
            data = load_file(fname)
            disabled = ""
            html = load_file("html/file_form.html")
            html = html.format(disabled=disabled, file_name=fname, file_data=data)
            self.send_hdr()
            self.wfile.write(html.encode())


def run_web_config_server():
    # noinspection PyTypeChecker
    server = HTTPServer(("", LOCAL_PORT), ConfigHandler)
    MY_LOG.warning(f"HTTP server starting at: {LOCAL_IP}:")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    run_web_config_server()
