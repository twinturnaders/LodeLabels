from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime


HOST = "127.0.0.1"
PORT = 8765


class SaleHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        print(
            f"[{datetime.now()}] OPTIONS received",
            flush=True
        )

        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "https://www.whatnot.com"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()


    def do_POST(self):

        print(
            f"[{datetime.now()}] POST received: {self.path}",
            flush=True
        )

        if self.path != "/sale":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        username = body.decode("utf-8").strip()

        print(
            f"RAW BODY: {body!r}",
            flush=True
        )

        print()
        print("==============================", flush=True)
        print(
            f"SALE RECEIVED: {username}",
            flush=True
        )
        print("==============================", flush=True)
        print()

        self.send_response(200)

        self.send_header(
            "Access-Control-Allow-Origin",
            "https://www.whatnot.com"
        )

        self.send_header(
            "Content-Type",
            "text/plain"
        )

        self.end_headers()

        response = f"LODELABELS_RECEIVED:{username}"

        self.wfile.write(
            response.encode("utf-8")
        )


    def log_message(self, format, *args):
        return


server = ThreadingHTTPServer(
    (HOST, PORT),
    SaleHandler
)

print("=================================", flush=True)
print("LODELABELS DIAGNOSTIC LISTENER", flush=True)
print(f"http://{HOST}:{PORT}", flush=True)
print("=================================", flush=True)

server.serve_forever()