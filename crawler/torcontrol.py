import time
import requests
import logging
import sys
from fake_useragent import UserAgent
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

    def switch_circuits(self):
        while True:
            headers = {'User-Agent': UserAgent().random}
            current_second = time.localtime().tm_sec
            if current_second in {0, 30}:
                with Controller.from_port(port=9051) as control:
                    control.authenticate(password=c.ADMIN_PASS)
                    control.signal(Signal.NEWNYM)
                    new_ip = requests.get('https://checkip.amazonaws.com/',
                                          proxies=self.proxies, headers=headers).text
                    logging.info(f"Your IP is : {new_ip}")
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
