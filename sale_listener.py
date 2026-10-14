from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


HOST = "127.0.0.1"
PORT = 8765


def start_sale_listener(on_sale):

    class SaleHandler(BaseHTTPRequestHandler):

        def do_OPTIONS(self):
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

            if self.path != "/sale":
                self.send_response(404)
                self.end_headers()
                return

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            )

            username = (
                body
                .decode("utf-8")
                .strip()
            )

            if not username:
                self.send_response(400)
                self.end_headers()
                return

            print(
                f"Whatnot sale received: "
                f"{username}"
            )

            try:
                on_sale(username)

            except Exception as error:
                print(
                    "Error processing "
                    f"Whatnot sale: {error}"
                )

                self.send_response(500)

                self.send_header(
                    "Access-Control-Allow-Origin",
                    "https://www.whatnot.com"
                )

                self.end_headers()

                return

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

            self.wfile.write(b"OK")


        def log_message(
            self,
            format,
            *args
        ):
            return


    server = ThreadingHTTPServer(
        (HOST, PORT),
        SaleHandler
    )

    thread = Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    print(
        f"LodeLabels listener running "
        f"on http://{HOST}:{PORT}"
    )

    return server