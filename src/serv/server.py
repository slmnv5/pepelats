from http.server import BaseHTTPRequestHandler, HTTPServer

from utils.utillog import MyLog


class MyHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        MyLog().info(f"GET request,\nPath: {self.path}\nHeaders:\n{self.headers}\n")
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        MyLog().info(f"POST:\nPath: {self.path}\nHeaders:\n{self.headers}\n\nBody:\n{post_data.decode('utf-8')}")

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def server_start():
    httpd = HTTPServer(('', 8000), MyHandler)
    MyLog().info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    MyLog().info('Stopping httpd...\n')


if __name__ == '__main__':
    server_start()
