#!/usr/bin/python3

import os
import sys
import sqlite3
from multiprocessing import Process
from proxy_dns_collector.configparser import load_config
from proxy_dns_collector.logger import setup_logger
from proxy_dns_collector.dnsutils import handle_dns_request
from scapy.all import sniff, DNSQR


WORKDIR = os.path.dirname(os.path.realpath(__file__))
CONFIGDIR = os.path.join(WORKDIR, "config")
LOGDIR = os.path.join(WORKDIR, "log")
DB_FILE = os.path.join(WORKDIR, "requests.db")

if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)


def initialize_database() -> None:
    try:
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dns_requests (
                id INTEGER PRIMARY KEY,
                query TEXT UNIQUE
            )
        """)
        base_logger.debug("Database initialized successfully.")
    except sqlite3.Error as err:
        db_logger.error("Database initialized error: {}".format(err))


def dns_sniffer(packet) -> None:
    try:
        if packet.haslayer(DNSQR):
            query: str = packet[DNSQR].qname.decode().rstrip(".")
            client_process = Process(
                target=handle_dns_request, args=(query, config_values, DB_FILE))
            client_process.start()
            client_process.join()
    except Exception as err:
        raise ValueError("Error in dns_sniffer: {}".format(err))


def main(config: dict) -> None:
    try:
        bind9_port = config["bind9_port"]

        filter = "udp port {}".format(bind9_port)

        try:
            base_logger.info(
                "DNS proxy request collector is running - listen port:{}".format(bind9_port))
            sniff(iface="eth0", filter=filter, prn=dns_sniffer, store=0)
        except Exception as err:
            raise ValueError("Error in sniff: {}".format(err))

    except KeyboardInterrupt:
        base_logger.exception(
            "Process interrupted by user (Ctrl+C). Exiting...")
        sys.exit(0)
    except Exception as err:
        raise ValueError("Error in main block: {}".format(err))


if __name__ == "__main__":
    try:
        config_logger = setup_logger(name="config_logger", log_file=os.path.join(LOGDIR, "base_logger.log"), level="INFO")

        config = load_config(config_dir=CONFIGDIR)
        config_values = {
            "logger_level": config.get("logger", "level", fallback="INFO"),
            "bind9_address": config.get("bind9", "address", fallback="127.0.0.1"),
            "bind9_port": config.getint("bind9", "port", fallback=53),
            "filter_pattern": "|".join(config.get("filter", "pattern", fallback="").split(", ")),
            "api_host": config.get("api", "host"),
            "api_username": config.get("api", "username"),
            "api_password": config.get("api", "password"),
            "api_port": config.getint("api", "port", fallback=8728),
            "address_list": config.get("api", "address_list"),
            "api_comment": config.get("api", "comment"),
        }

        base_logger = setup_logger(name="base_logger", log_file=os.path.join(LOGDIR, "base_logger.log"),
            level=config_values["logger_level"])
        db_logger = setup_logger(name="db_logger", log_file=os.path.join(LOGDIR, "db_logger.log"), 
            level=config_values["logger_level"])
        api_logger = setup_logger(name="api_logger", log_file=os.path.join(LOGDIR, "api_logger.log"),
            level=config_values["logger_level"])

        base_logger.debug("Initialize database: {}".format(DB_FILE))
        initialize_database()

        base_logger.debug(
            "Starting DNS proxy with config: {}".format(config_values))
        main(config_values)
    except Exception as err:
        msg_err = "An unexpected error occurred: {}".format(err)
        print(msg_err)
        base_logger.error(msg_err)
        sys.exit(1)
