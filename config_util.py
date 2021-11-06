import configparser

config = configparser.ConfigParser()
config.read('dev_config.ini')


def get(key: str) -> str:
    return config[key]


def set_config(key: str, new_val: str) -> bool:
    config[key] = new_val
    return True
