#!/usr/bin/env python3
import sys
import asyncio
import argparse
from utils.logger_conifg import get_scanner_logger

logger = get_scanner_logger()


class AsyncPortScanner:
    PROBES = {
        "MQTT": b"\x10\x0c\x00\x04MQTT\x04\x02\x00\x00\x00\x00",
        "HTTP": b"HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n",
        "GENERIC": b"\r\n"
    }

    def __init__(self, target: str, timeout: float = 1.0):
        self.target = target
        self.timeout = timeout

    async def grab_info(self, reader, writer, port: int) -> str:
        """Versucht Informationen über den Dienst zu erhalten."""
        try:
            # Sende Stupser
            if port == 1883:
                writer.write(self.PROBES["MQTT"])
            elif port in [80, 8080, 3000]:
                writer.write(self.PROBES["HTTP"])
            else:
                writer.write(self.PROBES["GENERIC"])

            await writer.drain()

            # Lese Antwort (Das Banner vom Server)
            data = await asyncio.wait_for(reader.read(1024), timeout=1.5)

            if not data: return "Kein Banner"

            decoded = data.decode('utf-8', errors='ignore').strip()
            # Falls unser Server gefunden wurde, nehmen wir die erste Zeile
            return decoded.split('\n')[0][:50]
        except Exception:
            return "Timeout beim Probing"

    async def scan_port(self, port: int) -> dict:
        try:
            conn = asyncio.open_connection(self.target, port)
            reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)

            info = await self.grab_info(reader, writer, port)

            writer.close()
            await writer.wait_closed()

            logger.info(f"Port {port:5} [OPEN] - Info: {info}")
            return {port: {"status": "OPEN", "info": info}}
        except:
            return {port: {"status": "CLOSED", "info": "-"}}

    async def run_scan(self, start: int, end: int):
        logger.info(f"Starte Profi-Scan auf {self.target} ({start}-{end})...")
        tasks = [self.scan_port(p) for p in range(start, end + 1)]
        results = await asyncio.gather(*tasks)
        return results


async def main_async(args: argparse.Namespace) -> int:
    scanner = AsyncPortScanner(args.target, args.timeout)
    await scanner.run_scan(args.start, args.end or args.start)
    return 0


def cli() -> int:
    parser = argparse.ArgumentParser(description="Async Port Scanner")
    parser.add_argument("target")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int)
    parser.add_argument("--timeout", type=float, default=1.0)
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(cli())