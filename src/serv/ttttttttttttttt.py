import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

IP_ADDRESS = "192.168.1.1"  # subprocess.check_output("hostname -I", shell=True)
BASE_DIR = None
LOAD_PREFIX = "/load?file="

MAIN_HTML = """
<html>
<style>
h1 {text-align:center;}
p {text-align:center;}
table, th, td {
border: 5px solid grey; padding: 15px; text-align: left;
}
</style>
<head>
</head>
<body>
<table style="width:100%%">
<tr><td><h1>Selected files</h1></td><td><h1>All files</h1></td></tr>
<tr><td>%s</td><td>%s</td></tr>
</table>
</body>
</html>
"""

REDIRECT_HTML = """
<html>
<head>
	<meta http-equiv="refresh" content="0; url=http://%s:%s/login" />
</head>
<body>
	<b>Redirecting to login page</b>
</body>
</html>
""" % (IP_ADDRESS, 8000)

FILE_HTML = """
<html>
<style>
iframe { 
   position: absolute; 
   top: 3%%; 
   left:3%%; 
   width: 95%%; 
   height: 95%%;
} 
</style>
<head>
</head>
<body>
<iframe id="myFrame" src="%s"></iframe>

<script>
var frame = document.getElementById('myFrame');
	frame.onload = function () {
		var body = frame.contentWindow.document.querySelector('body');
		body.style.color = 'black';
		body.style.fontSize = '2vw';
	 };
</script>

</body>
</html>
"""


def recursive_files(dname: str) -> list[str]:
    def match_file(x: str) -> bool:
        return x.endswith(".ini") or x.endswith(".txt")

    files1 = [r + os.sep + f for (r, _, f) in os.walk(".") if match_file(f)]
    files2 = [r + os.sep + f for (r, _, f) in os.walk("./config") if match_file(f)]
    return [*files1, *files2]


class MyHandler(BaseHTTPRequestHandler):

    def send_load(self):
        self.send_head()
        filename = self.path[len(LOAD_PREFIX):]
        str1 = "./" + filename
        str2 = FILE_HTML % (str1)
        self.wfile.write(bytes(str2))

    def send_main(self):
        self.send_head()
        str1 = MAIN_HTML % ("dddddddddddddddddd", "wwwweeeeeeeeeeeee")
        self.wfile.write(bytes(str1))

    def send_binary(self, filename):
        f = open(filename, "rb")
        str1 = f.read()
        f.close()
        self.wfile.write(str1)

    def send_redir(self):
        self.send_head()
        self.wfile.write(REDIRECT_HTML)

    def send_head(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith(LOAD_PREFIX):
            return self.send_load()

        if self.path.startswith("/login"):
            return self.send_main()

        isLocal = self.path.startswith("/")
        fileExists = os.path.isfile("." + self.path)
        if isLocal and fileExists:
            return self.send_binary("." + self.path)

        return self.send_redir()


if __name__ == '__main__':

    IP_TABLES_COMMANDS = []
    BASE_DIR = os.path.expanduser("~/Dropbox/mypi/music")
    if not os.path.isdir(BASE_DIR):
        BASE_DIR = os.path.expanduser("~/mypi/music")
        if not os.path.isdir(BASE_DIR):
            sys.exit("Root directory not found: " + BASE_DIR)

    SAVEPATH = os.getcwd()
    os.chdir(BASE_DIR)
    print(11111111111111)
    os.getcwd(), SAVEPATH

    my_serv1 = HTTPServer(('', 8000), MyHandler)

    try:
        my_serv1.serve_forever()
    except KeyboardInterrupt:
        print("closed")

    my_serv1.server_close()

    os.chdir(SAVEPATH)
