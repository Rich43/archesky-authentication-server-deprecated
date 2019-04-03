from configparser import ConfigParser
from os.path import exists


def load_config():
    error = 'Missing config.ini, try renaming config_example.ini?'
    assert exists('config.ini'), error
    config = ConfigParser()
    config.read('config.ini')
    return config['app:main']
