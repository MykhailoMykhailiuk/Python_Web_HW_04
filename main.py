from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import mimetypes
from pathlib import Path
from threading import Thread
import socket
from datetime import datetime
import json


class HttpGetHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, ('localhost', 5000))
        sock.close()
        self.send_response(302)
        self.send_header('Location', '/message.html')
        self.end_headers()

    def do_GET(self):
        url = parse.urlparse(self.path)
        if url.path == '/':
            self.send_html('index.html')
        elif url.path == '/message.html':
            self.send_html('message.html')
        else:
            p = Path(url.path[1:])
            if p.exists():
                self.send_static(str(p))
            else:
                self.send_html('error.html', 404)

    def send_html(self, html_filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(html_filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_static(self, static_filename):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header('Content-type', mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(static_filename, 'rb') as f:
            self.wfile.write(f.read())
            

def run(server_class=HTTPServer, handler_class=HttpGetHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        
        
def run_server(ip='localhost', port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    while True:
        data, address = sock.recvfrom(1024)
        data_parse = parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        json_dict = {}
        time = datetime.now()
        json_dict[str(time)] = data_dict
        with open('storage/data.json', 'a') as f:
            json.dump(json_dict, f, indent=4)


if __name__ == '__main__':
    th1 = Thread(target=run)
    th2 = Thread(target=run_server)

    th1.start()
    th2.start()

    th1.join()
    th2.join()

