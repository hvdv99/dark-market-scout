class Crawler:
    def __init__(self):
        self.cookies = list()
        self.seed = set()
        self.exit_condition = bool()
        self.request_interval = 1
        self.request_timing = 'constant'

    def set_cookies(self, cookies: list):
        if not isinstance(cookies, list):
            return TypeError('Cookies should be inserted as list')
        else:
            self.cookies = cookies

    def set_seed(self, seed: str | list):
        if not isinstance(seed, str) or not isinstance(seed, list):
            return TypeError('Seed should either be list or string')
        if isinstance(seed, list):
            for s in seed:
                self.seed.add(s)
        else:
            self.seed.add(seed)

    def set_exit_condition(self, condition: bool):
        if not isinstance(condition, bool):
            return TypeError('Condition is not of type bool')
        else:
            self.exit_condition = condition

    def set_request_interval(self, new_interval: int):
        if not isinstance(new_interval, int):
            return TypeError('Interval should be of type integer')
        if new_interval < 0:
            return ValueError('Interval should be positive or zero')
        self.request_interval = new_interval

    def set_request_timing_behaviour(self, new_timing_behaviour):
        timing_types = {'constant', 'random'}
        if not isinstance(new_timing_behaviour, str):
            return TypeError('Timing should be of type string')
        if new_timing_behaviour not in timing_types:
            return ValueError('Timing should either be constant or random')
        self.request_timing = new_timing_behaviour

    def set_user_agent_behaviour(self):
        pass

    def send_request(self):
        pass

    def detect_captcha(self) -> bool:
        pass

    def _extract_internal_links(self):
        pass

    def crawl(self):
        pass

    def _save_resource(self):
        pass

    def _sync_resources(self):
        pass
