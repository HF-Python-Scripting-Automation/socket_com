#!/usr/bin/env python3
import sys
import json
import socket
import argparse
import traceback
from cryptography.fernet import Fernet
from utils.logger_conifg import get_server_logger

logger = get_server_logger()


class JsonServer:
    def __init__(self, host: str, port: int, key_path: str = "secret.key", encrypt: bool = True):
        self.address = (host, port)
        self.encoding = 'utf-8'
        self.delimiter = b'\n'
        self.encrypt = encrypt
        self.fernet = None

        if self.encrypt:
            try:
                with open(key_path, "rb") as f:
                    self.fernet = Fernet(f.read())
            except FileNotFoundError:
                logger.error(f"Key-Datei {key_path} nicht gefunden!")
                raise

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.address)
            sock.listen(5)
            mode = "VERSCHLÜSSELT" if self.encrypt else "KLARTEXT"
            logger.info(f"Server ({mode}) gestartet auf {self.address}")

            while True:
                conn, addr = sock.accept()
                self._handle_client(conn, addr)

    def _handle_client(self, conn, addr):
        with conn:
            conn.settimeout(2.0)
            logger.info(f"Verbindung von {addr}")

            # NEU: Sofortiges Senden eines Banners für den Port-Scanner
            banner = f"JSON-Server 1.0 (Auth: {self.encrypt})".encode(self.encoding)
            try:
                conn.sendall(banner + self.delimiter)
            except Exception as e:
                logger.warning(f"Konnte Banner nicht an {addr} senden: {e}")
                return

            try:
                buffer = bytearray()
                while True:
                    chunk = conn.recv(4096)
                    if not chunk: break
                    buffer.extend(chunk)
                    if self.delimiter in buffer: break

                if not buffer: return

                raw_payload = buffer.split(self.delimiter)[0]

                if self.encrypt:
                    decrypted_bytes = self.fernet.decrypt(bytes(raw_payload))
                    message = json.loads(decrypted_bytes.decode(self.encoding))
                else:
                    message = json.loads(raw_payload.decode(self.encoding))

                for k, v in message.items():
                    logger.info(f"  {k}: {v}")

                response = hex(len(raw_payload)).encode(self.encoding)
                conn.sendall(response)

            except Exception as e:
                logger.error(f"Fehler bei Datenverarbeitung von {addr}: {e}")
                # Optional: Fehler-Banner für den Scanner
                error_info = f"ERR: {type(e).__name__}".encode(self.encoding)
                conn.sendall(error_info + self.delimiter)


def main(args: argparse.Namespace) -> int:
    try:
        server = JsonServer(args.host, args.port, encrypt=not args.no_encrypt)
        server.run()
        return 0
    except Exception:
        print("\n[Server Crash]", file=sys.stderr)
        traceback.print_exc()
        return -1


def cli() -> int:
    parser = argparse.ArgumentParser(description="Secure JSON TCP Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6543)
    parser.add_argument("--no-encrypt", action="store_true", help="Deaktiviert die Verschlüsselung")
    return main(parser.parse_args())


if __name__ == "__main__":
    try:
        sys.exit(cli())
    except KeyboardInterrupt:
        logger.info("Server beendet.")
        sys.exit(0)