import routeros_api
import routeros_api.exceptions
from typing import Set
import logging
from proxy_dns_collector.logger import CURRENT_USER

base_logger = logging.getLogger("base_logger")
base_logger = logging.LoggerAdapter(base_logger, {"user": CURRENT_USER})

api_logger = logging.getLogger("api_logger")
api_logger = logging.LoggerAdapter(api_logger, {"user": CURRENT_USER})


def connect_to_api(host: str, username: str, password: str, port: int) -> routeros_api.RouterOsApiPool:
    try:
        connection_api = routeros_api.RouterOsApiPool(
            host, username=username, password=password, port=port, plaintext_login=True
        )
        base_logger.debug("Connected to MikroTik API successfully.")

        return connection_api

    except routeros_api.exceptions.RouterOsApiConnectionError as err:
        msg_err = "Failed to connect to MikroTik API: {}".format(err)
        api_logger.error(msg_err)
        raise ValueError(msg_err)
    except Exception as err:
        msg_err = "An unexpected error occurred in connect to api: {}".format(
            err)
        base_logger.error(msg_err)
        raise ValueError(msg_err)


def add_to_address_list(api: routeros_api.RouterOsApiPool, queries: Set[str], address_list: str, comment: str) -> bool:
    try:
        _api = api.get_api()
    except Exception as err:
        msg_err = "An unexpected error occurred in add to address: {}".format(
            err)
        base_logger.error(msg_err)
        raise ValueError(msg_err)

    for query in queries:
        try:
            _api.get_resource("/ip/firewall/address-list").add(
                address=query,
                list=address_list,
                comment=comment
            )
            api_logger.info("Added {} to MikroTik address list.".format(query))

            return True

        except routeros_api.exceptions.RouterOsApiCommunicationError as err:
            api_logger.error("Failed to add {}: {}".format(query, err))
        except Exception as err:
            msg_err = "An unexpected error occurred in add to address: {}".format(
                err)
            base_logger.error(msg_err)
            raise ValueError(msg_err)
