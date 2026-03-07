import logging
from psa_utils.logger import get_logger, configure_logging


configure_logging(log_dir="logs", clear_old_logs=True)
server_logger = get_logger("Server", filename="server.log", level=logging.DEBUG)
client_logger = get_logger("Client", filename="client.log", level=logging.DEBUG)