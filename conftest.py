import sys

def pytest_configure(config):
    sys._is_a_test = True