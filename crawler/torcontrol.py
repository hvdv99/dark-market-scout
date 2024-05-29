import time
import logging
import sys
from stem import Signal
from stem.control import Controller

from config import constants as c


class TorCircuitSwitcher:

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    def __init__(self):
        self.proxies = {
            'http': 'socks5h://localhost:9050',
            'https': 'socks5h://localhost:9050'
        }

    @staticmethod
    def switch_circuits():
        while True:
            current_second = time.localtime().tm_sec
            if current_second in {0, 30}:
                with Controller.from_port(port=9051) as control:
                    control.authenticate(password=c.ADMIN_PASS)
                    control.signal(Signal.NEWNYM)
                    logging.info('Tor: got new circuit')
                    time.sleep(1)
            elif current_second > 30:
                logging.info('sleeping > 30')
                time.sleep(60 - current_second)
            elif current_second < 30:
                logging.info('sleeping < 30')
                time.sleep(30 - current_second)


if __name__ == "__main__":
    tctswitcher = TorCircuitSwitcher()
    tctswitcher.switch_circuits()
