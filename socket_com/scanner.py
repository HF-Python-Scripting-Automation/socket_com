#!/usr/bin/env python3
import sys
import socket
import errno
import argparse
import traceback
from utils.logger_conifg import get_scanner_logger

# Globaler Logger für das Modul
logger = get_scanner_logger()


class PortScanner:
    def __init__(self, target: str, timeout: float = 0.2):
        self.target = target
        self.timeout = timeout
        self.error_descriptions = {
            errno.ECONNREFUSED: "Port geschlossen oder Verbindung abgelehnt.",
            errno.ETIMEDOUT: "Zeitüberschreitung (Firewall oder Host down).",
            errno.ENETUNREACH: "Netzwerk nicht erreichbar.",
            errno.EHOSTUNREACH: "Host nicht erreichbar.",
        }

    def scan(self, start_port: int, end_port: int = None) -> dict:
        """Führt den Scan für einen Bereich oder einen einzelnen Port aus."""
        results = {}
        end = end_port if end_port else start_port

        logger.info(f"Scanning {self.target} von Port {start_port} bis {end}...")

        for port in range(start_port, end + 1):
            results[port] = self._check_port(port)
        return results

    def _check_port(self, port: int) -> dict:
        """Interner Check für einen einzelnen Port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(self.timeout)
            result_code = s.connect_ex((self.target, port))

            res = {
                'available': result_code == 0,
                'error_id': result_code if result_code != 0 else None,
            }

            # Optional: Logge jeden Treffer sofort
            if res['available']:
                logger.info(f"Gefunden: Port {port} ist OFFEN")

            return res

    def log_report(self, results: dict):
        """Loggt den fertigen Report über den Logger."""
        logger.info(f"--- Scan Report für {self.target} ---")
        for port, data in results.items():
            if data['available']:
                status = "OFFEN"
                logger.info(f"Port {port:5}: {status}")
            else:
                e_id = data['error_id']
                error_name = errno.errorcode.get(e_id, 'Unbekannter Fehler')
                desc = self.error_descriptions.get(e_id, "Keine detaillierte Beschreibung verfügbar.")
                status = f"GESCHLOSSEN [EID: {e_id} | {error_name}]: {desc}"
                # Geschlossene Ports als Debug, um das Info-Log sauber zu halten
                logger.debug(f"Port {port:5}: {status}")


def main(args: argparse.Namespace) -> int:
    try:
        scanner = PortScanner(args.target, args.timeout)
        results = scanner.scan(args.start, args.end)
        scanner.log_report(results)
        return 0
    except Exception as e:
        logger.error(f"Scanner Crash: {e}")
        # Traceback wird ebenfalls über den Logger geloggt
        logger.error(traceback.format_exc())
        return -1


def cli() -> int:
    parser = argparse.ArgumentParser(description="Python Port Scanner CLI")
    parser.add_argument("target", help="Ziel IP-Adresse oder Hostname")
    parser.add_argument("--start", type=int, default=1, help="Start Port (Default: 1)")
    parser.add_argument("--end", type=int, help="End Port (Optional)")
    parser.add_argument("--timeout", type=float, default=0.2, help="Timeout (Sekunden)")

    return main(parser.parse_args())


if __name__ == "__main__":
    try:
        sys.exit(cli())
    except KeyboardInterrupt:
        logger.info("Scan durch Benutzer beendet.")
        sys.exit(0)