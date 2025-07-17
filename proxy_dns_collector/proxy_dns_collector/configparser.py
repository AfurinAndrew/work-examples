import os
import sys
import configparser
import logging
from proxy_dns_collector.logger import CURRENT_USER

config_logger = logging.getLogger("config_logger")
config_logger = logging.LoggerAdapter(config_logger, {"user": CURRENT_USER})


def load_config(config_file: str = "config.ini", config_dir: str = None) -> configparser.ConfigParser:
    if config_dir:
        config_file_path = os.path.join(config_dir, config_file)
    else:
        config_file_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), config_file)

    if not os.path.exists(config_file_path):
        msg_err = "Configuration file not found at: {}".format(
            config_file_path)
        print(msg_err)
        config_logger.error(msg_err)
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_file_path)

    return config
