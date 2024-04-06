class CaptchaDetector:
    """
    CaptchaDetector class is used to detect if a scraped html page contains a captcha instead of the expected content.
    ...
    Attributes
    ----------
    captcha_fingerprints: list
        A list of strings that are used to detect if a page contains a captcha.
    ...
    Methods
    ----------
    detect_captcha(html: str) -> bool
        This method detects if a scraped html page contains a captcha instead of the expected content.
    """

    def __init__(self):
        self.captcha_fingerprints = ["Strike", "Strikes", "Security breach detected", "Captcha",
                                     "ddos 2-factor-protection"]

    def detect_captcha(self, html: str) -> bool:
        """This method detects if a scraped html page contains a captcha instead of the expected content.
        args:
            html: str: The html content of the scraped page.
        returns:
            bool: True if the page contains a captcha, False otherwise.
        """
        #TODO: Implement a more sophisticated way to detect captchas.
        # Currently, it just checks if the html contains any of the predefined captcha fingerprints.
        # But we want to have a pipeline of some sort that combines multiple methods to detect captchas.
        # First, need to gather more data on how captchas are implemented on different websites.
        return self._find_fingerprint(html)

    def _find_fingerprint(self, html: str) -> bool:
        """Finds if a Captcha fingerprint is present in the html content"""
        for fingerprint in self.captcha_fingerprints:
            if fingerprint.lower() in html.lower():
                return True
        return False
