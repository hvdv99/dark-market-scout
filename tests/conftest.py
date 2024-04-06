import pytest


@pytest.fixture
def load_html():
    def _loader(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    return _loader