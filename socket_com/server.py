#!/usr/bin/env python3
import sys
import json
import socket
import argparse
import traceback
from utils.logger_conifg import get_server_logger
logger = get_server_logger()


class JsonServer:
    def __init__(self, host: str, port: int):
        self.address = (host, port)
        self.encoding = 'utf-8'
        self.delimiter = b'\n'

    def run(self):
        """Hauptloop des Servers."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.address)
            sock.listen(5)
            logger.info(f"Server gestartet auf {self.address}")

            while True:
                conn, addr = sock.accept()
                self._handle_client(conn, addr)

    def _handle_client(self, conn, addr):
        with conn:
            conn.settimeout(2.0)
            logger.info(f"Verbindung von {addr}")
            try:
                buffer = bytearray()
                while True:
                    chunk = conn.recv(4096)
                    if not chunk: break
                    buffer.extend(chunk)
                    if self.delimiter in buffer: break

                if not buffer: return

                # Logik: Daten verarbeiten
                msg_bytes = buffer.split(self.delimiter)[0]
                message = json.loads(msg_bytes.decode(self.encoding))

                for k, v in message.items():
                    logger.info(f"  {k}: {v}")

                # Antwort senden (Länge in Hex)
                response = hex(len(msg_bytes)).encode(self.encoding)
                conn.sendall(response)

            except Exception as e:
                logger.error(f"Fehler bei Client {addr}: {e}")


def main(args: argparse.Namespace) -> int:
    try:
        server = JsonServer(args.host, args.port)
        server.run()
        return 0
    except Exception:
        print("\n[Server Crash]", file=sys.stderr)
        traceback.print_exc()
        return -1


def cli() -> int:
    parser = argparse.ArgumentParser(description="JSON TCP Server")
    parser.add_argument("--host", default="192.168.110.04", help="Listening Host")
    parser.add_argument("--port", type=int, default=6543, help="Listening Port")
    return main(parser.parse_args())


if __name__ == "__main__":
    try:
        sys.exit(cli())
    except KeyboardInterrupt:
        logger.info("Server durch Benutzer beendet.")
        sys.exit(0)