import json
import socket

server_address = ('127.0.0.1', 6543)
ENCODING = 'utf-8'
DELIMITER = '\n'
DELIMITER_BYTES = DELIMITER.encode(ENCODING)
DT_FMT = '%d.%m.%Y %H:%M:%S'




try:
   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
       server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       server_socket.bind(server_address)
       server_socket.listen(1)
       print(f'Server auf {server_address[0]}:{server_address[1]} gestartet')

       while True:
           print('\nWarte auf eingehende Verbindung...')
           try:
               connection, client_address = server_socket.accept()
               print(f'\t- Verbindung akzeptiert von {client_address}, lese Buffer')
               connection.settimeout(2)
               with connection:
                   buffer = bytearray()
                   try:
                       while True:
                           chunk = connection.recv(1024)
                           if not chunk:
                               break
                           buffer.extend(chunk)
                           delim_pos = buffer.find(DELIMITER_BYTES)
                           if delim_pos != -1:
                               message_bytes = bytes(buffer[:delim_pos])
                               break
                       if not buffer:
                           print('Server: Keine Daten empfangen.')
                       elif buffer.find(DELIMITER_BYTES) == -1:
                           print('Server: Nachricht unvollständig (Delimiter nicht empfangen).')
                       else:
                           try:
                               message = json.loads(message_bytes.decode(ENCODING))
                               for k, v in message.items():
                                   print(f'\t- {k}: {v}')
                           except UnicodeDecodeError as e:
                               print(
                                   'Server hat Message empfangen, aber konnte diese nicht lesen, Fehler: '
                                   f'{e.__class__.__name__} {e}'
                               )
                   except Exception as e:
                       print(
                           'Server: Fehler beim Empfangen der Daten, Fehler: '
                           f'{e.__class__.__name__} {e}'
                       )
                   try:
                       response = hex(len(message_bytes))
                       connection.sendall(response.encode(ENCODING))
                   except Exception as e:
                       print(f'Fehler beim Senden: {e.__class__.__name__} {e}')
           except Exception as e:
               print(f'\t- Fehler im Verbindungs-Loop: {e.__class__.__name__} {e}')
except Exception as e:
   print(f'Ein Fehler ist aufgetretten: {e.__class__.__name__} {e}')