import re
import sqlite3
import logging
from proxy_dns_collector.logger import CURRENT_USER
from proxy_dns_collector.mikrotik import connect_to_api, add_to_address_list

base_logger = logging.getLogger("base_logger")
base_logger = logging.LoggerAdapter(base_logger, {"user": CURRENT_USER})

db_logger = logging.getLogger("db_logger")
db_logger = logging.LoggerAdapter(db_logger, {"user": CURRENT_USER})

api_logger = logging.getLogger("api_logger")
api_logger = logging.LoggerAdapter(api_logger, {"user": CURRENT_USER})


def handle_dns_request(query: str, config: dict, db_file: str) -> None:
    api_config = {
        "api_host": config["api_host"],
        "api_username": config["api_username"],
        "api_password": config["api_password"],
        "api_port": config["api_port"],
        "address_list": config["address_list"],
        "api_comment": config["api_comment"],
        "filter_pattern": config["filter_pattern"],
    }

    try:
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        base_logger.debug("Connected to the database.")

        extract_and_store_dns_queries(query, cursor, api_config)
        base_logger.debug("DNS queries extracted and stored (if any).")

        connection.commit()
        base_logger.debug("Changes committed to the database.")

    except sqlite3.Error as err:
        raise ValueError("SQLite error: {}".format(err))
    except Exception as err:
        raise ValueError("Error handling DNS request: {}".format(err))
    finally:
        if "connection" in locals():
            connection.close()
            base_logger.debug("Database connection closed.")


def extract_and_store_dns_queries(query: str, cursor: sqlite3.Cursor, api_config: dict) -> None:
    try:
        base_logger.debug("Starting extraction and storage of DNS queries.")

        existing_queries = set()
        cursor.execute("SELECT query FROM dns_requests;")
        existing_queries.update(row[0] for row in cursor.fetchall())
        base_logger.debug(
            "Loaded {} existing queries from the database.".format(len(existing_queries)))

        base_logger.debug("DNS request: domain={}".format(query))

        unique_queries = set()
        if query is not None and re.search(api_config["filter_pattern"], query) and query not in existing_queries:
            unique_queries.add(query)
            base_logger.debug("Found new unique query: {}".format(query))

        if unique_queries:
            try:
                base_logger.debug(
                    "Connecting to MikroTik API to add {} queries.".format(len(unique_queries)))

                api = connect_to_api(
                    api_config["api_host"],
                    api_config["api_username"],
                    api_config["api_password"],
                    api_config["api_port"]
                )

                if add_to_address_list(api, unique_queries, api_config["address_list"], api_config["api_comment"]):
                    for query in unique_queries:
                        cursor.execute(
                            "INSERT INTO dns_requests (query) VALUES (?);", (query,))
                        db_logger.info(
                            "Added new query to database: {}".format(query))
                        base_logger.debug(
                            "Stored query in database: {}".format(query))

            except Exception as err:
                api_logger.error(
                    "Failed to connect to MikroTik API: {}".format(err))
            finally:
                if "connection_api" in locals():
                    api.disconnect()
                    base_logger.debug("Disconnected from MikroTik API.")
        else:
            base_logger.debug("No new unique queries found to process.")

    except Exception as err:
        raise ValueError(
            "An unexpected error occurred in extract and store: {}".format(err))
