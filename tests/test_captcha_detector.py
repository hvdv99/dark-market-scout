import pytest
import os
from captcha.detector import CaptchaDetector


def list_html_files(directory):
    """Lists all HTML files in the given directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of the current file
    full_path = os.path.join(base_dir, directory)  # Builds the full path to the data directory
    return [os.path.join(full_path, f) for f in os.listdir(full_path) if f.endswith('.html')]


@pytest.mark.parametrize("file_path", list_html_files('data/captcha/'))
def test_detects_captcha(load_html, file_path):
    html_captcha = load_html(file_path)
    detector = CaptchaDetector()
    assert detector.detect_captcha(html_captcha) is True


@pytest.mark.parametrize("file_path", list_html_files('data/non_captcha/'))
def test_detects_non_captcha(load_html, file_path):
    html_non_captcha = load_html(file_path)
    detector = CaptchaDetector()
    assert detector.detect_captcha(html_non_captcha) is False
