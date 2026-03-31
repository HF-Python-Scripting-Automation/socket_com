#!/usr/bin/env python3
import sys
import json
import socket
import datetime
import time
import argparse
import traceback
from utils.logger_conifg import get_client_logger
logger = get_client_logger()



class JsonClient:
    def __init__(self, host: str, port: int, name: str):
        self.address = (host, port)
        self.name = name
        self.encoding = 'utf-8'
        self.delimiter = b'\n'

    def send(self, text: str) -> bool:
        payload = {
            'sender': self.name,
            'content': text,
            'timestamp': datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        }
        try:
            encoded = json.dumps(payload).encode(self.encoding)
            with socket.create_connection(self.address, timeout=5) as sock:
                sock.sendall(encoded + self.delimiter)

                raw_res = sock.recv(1024).decode(self.encoding).strip()
                if not raw_res: return False

                server_len = int(raw_res, 16)
                success = (len(encoded) == server_len)
                logger.info(f"Senden: {success} (Server: {server_len} Bytes)")
                return success
        except Exception as e:
            logger.error(f"Sende-Fehler: {e}")
            return False


def main(args: argparse.Namespace) -> int:
    try:
        client = JsonClient(args.host, args.port, args.name)
        for i in range(1, args.count + 1):
            content = f"Test-Nachricht {i}"
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
    parser.add_argument("-c", "--count", type=int, default=20, help="Anzahl Nachrichten")
    parser.add_argument("-d", "--delay", type=float, default=0.1, help="Pause zw. Nachrichten")
    parser.add_argument("--bloat", action="store_true", help="Sende extra große Datenmengen")
    return main(parser.parse_args())


if __name__ == "__main__":
    try:
        sys.exit(cli())
    except KeyboardInterrupt:
        sys.exit(130)