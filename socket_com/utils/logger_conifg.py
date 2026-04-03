import logging
from psa_utils.logger import get_logger

def get_server_logger():
    return get_logger("Server", filename="server.log", level=logging.DEBUG, clear=True)

def get_client_logger():
    return get_logger("Client", filename="client.log", level=logging.DEBUG, clear=True)

def get_scanner_logger():
    return get_logger("Scanner", filename="scanner.log", level=logging.DEBUG, clear=True)