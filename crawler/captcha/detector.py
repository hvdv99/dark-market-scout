import os
from bs4 import BeautifulSoup as bs

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB


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
        self.vectorizer = CountVectorizer()
        self.model = self._train_bayes()

    def detect_captcha(self, html: str) -> bool:
        """This method detects if a scraped html page contains a captcha instead of the expected content.
        args:
            html: str: The html content of the scraped page.
        returns:
            bool: True if the page contains a captcha, False otherwise.
        """
        return self._bayes_decide(html)

    def _find_fingerprint(self, html: str) -> bool:
        """Finds if a Captcha fingerprint is present in the html content"""
        for fingerprint in self.captcha_fingerprints:
            if fingerprint.lower() in html.lower():
                return True
        return False

    def _bayes_decide(self, html: str) -> bool:
        clean_html = self._parse_html(html=html)
        vectorized = self.vectorizer.transform([clean_html])
        prediction = self.model.predict(vectorized)
        if prediction == 'captcha':
            return True
        return False

    def _parse_html(self, html: str) -> str:
        page = bs(html, 'html.parser').text
        page = page.split('\n')

        while '' in page:
            page.remove('')
        page = ' '.join(page)
        page = page.split(' ')

        while '' in page:
            page.remove('')
        page = ' '.join(page)

        return page.lower().replace("\t", "").replace("\\", "").strip()

    def _load_data(self):
        train_data_dir = os.path.join('.', 'captcha', 'training-data')
        captcha_files = [os.path.join(train_data_dir, 'captcha', f) for f in
                         os.listdir(os.path.join(train_data_dir, 'captcha')) if f.endswith('.html')]
        non_captcha_files = [os.path.join(train_data_dir, 'non_captcha', f) for f in
                             os.listdir(os.path.join(train_data_dir, 'non_captcha')) if f.endswith('.html')]

        all_files = [captcha_files, non_captcha_files]

        result = list()
        for i, label in enumerate(['captcha', 'non-captcha']):
            for file in all_files[i]:
                with open(file, 'r') as f:
                    text = self._parse_html(f.read())
                    result.append((text, label))

        X, y = list(), list()
        for data, label in result:
            X.append(data)
            y.append(label)
        return X, y

    def _train_bayes(self):
        docs, labels = self._load_data()

        X = self.vectorizer.fit_transform(docs)

        model = ComplementNB()
        model.fit(X, labels)

        return model
