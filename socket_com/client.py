#!/usr/bin/env python3
import sys
import json
import socket
import datetime
import time
import argparse
import traceback
from cryptography.fernet import Fernet
from utils.logger_conifg import get_client_logger

logger = get_client_logger()


class JsonClient:
    def __init__(self, host: str, port: int, name: str, key_path: str = "secret.key", encrypt: bool = True):
        self.address = (host, port)
        self.name = name
        self.encoding = 'utf-8'
        self.delimiter = b'\n'
        self.encrypt = encrypt
        self.fernet = None

        if self.encrypt:
            with open(key_path, "rb") as f:
                self.fernet = Fernet(f.read())

    def send(self, text: str) -> bool:
        payload = {
            'sender': self.name,
            'content': text,
            'timestamp': datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        }
        try:
            raw_json = json.dumps(payload).encode(self.encoding)

            if self.encrypt:
                final_payload = self.fernet.encrypt(raw_json)
                mode_str = "Ciphertext"
            else:
                final_payload = raw_json
                mode_str = "Plaintext"

            with socket.create_connection(self.address, timeout=5) as sock:
                # NEU: Erst das Server-Banner lesen (da der Server jetzt zuerst sendet)
                server_banner = sock.recv(1024).decode(self.encoding).strip()

                sock.sendall(final_payload + self.delimiter)

                raw_res = sock.recv(1024).decode(self.encoding).strip()
                if not raw_res: return False

                server_reported_len = int(raw_res, 16)
                success = (len(final_payload) == server_reported_len)
                logger.info(f"Senden: {success} ({mode_str}: {len(final_payload)} Bytes)")
                return success
        except Exception as e:
            logger.error(f"Sende-Fehler: {e}")
            return False


def main(args: argparse.Namespace) -> int:
    try:
        client = JsonClient(args.host, args.port, args.name, encrypt=not args.no_encrypt)
        for i in range(1, args.count + 1):
            content = f"Nachricht {i}"
            if args.bloat:
                content += f" | Daten: {list(range(20)) * i}"
            client.send(content)
            time.sleep(args.delay)
        return 0
    except Exception:
        traceback.print_exc()
        return -1


def cli() -> int:
    parser = argparse.ArgumentParser(description="JSON TCP Client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6543)
    parser.add_argument("--name", default="Client_12421")
    parser.add_argument("-c", "--count", type=int, default=20)
    parser.add_argument("-d", "--delay", type=float, default=0.1)
    parser.add_argument("--bloat", action="store_true")
    parser.add_argument("--no-encrypt", action="store_true", help="Deaktiviert die Verschlüsselung")
    return main(parser.parse_args())


if __name__ == "__main__":
    try:
        sys.exit(cli())
    except KeyboardInterrupt:
        sys.exit(130)