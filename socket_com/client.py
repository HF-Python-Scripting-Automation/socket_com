import time
import json
import socket
import datetime

from utils.logger_conifg import client_logger as logger

server_address = ('127.0.0.1', 6543)
ENCODING = 'utf-8'
DELIMITER = '\n'
DELIMITER_BYTES = DELIMITER.encode(ENCODING)
CLIENT_NAME = 'Client Nr. 12421'
DT_FMT = '%d.%m.%Y %H:%M:%S'


def send_message(address: tuple[str, int], text: str) -> bool:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(address)
        message = {
            'sender': CLIENT_NAME,
            'content': text,
            'timestamp': datetime.datetime.now().strftime(DT_FMT),
        }
        encoded_message = json.dumps(message).encode(ENCODING)
        message_length = len(encoded_message)
        logger.info(f'Nachrichtenlänge: {message_length}')
        client_socket.sendall(encoded_message + DELIMITER_BYTES)
        response_length = int(client_socket.recv(1024).decode(ENCODING).strip(), 16)
        logger.info(f'Nachrichtenlänge beim Server: {response_length}')

        logger.info(f'Nachrichtenintegrität: {'Ja' if message_length == response_length else 'Nein'}')
        client_socket.close()
        return True
    except Exception as e:
        logger.error(f'Fehler beim Senden: {e.__class__.__name__} {e}')
    return False


for x in range(1, 21):
    send_message(server_address, f'Wir senden Nachricht {x} Bloat {[x for x in range(50)]*x}')
    time.sleep(0.1)

