# DNS Proxy Request Collector

## Description

The `proxy_dns_collector` script is a DNS proxy that:
1. Intercepts DNS requests on a specified port
2. Adds requested domains to a MikroTik address-list via API
3. Logs requests to an SQLite database
4. Provides flexible configuration and logging systems

## Features

- Multi-process DNS request handling
- Flexible file-based configuration
- Detailed logging to separate files
- SQLite database storage for requests
- Integration with MikroTik RouterOS API for adding domains to address-lists

## Requirements

### System Requirements
- Python 3.10 or higher
- Linux/Unix system (for best performance)
- Network interface with DNS traffic

### Python Dependencies
```bash
pip install scapy
```

## Configuration
Create config/config.ini with the following template:
```ini
[logger]
level = INFO  ; DEBUG, INFO, WARNING, ERROR, CRITICAL

[bind9]
address = 127.0.0.1
port = 53

[filter]
pattern = example.com, test.com  ; domains to filter (comma separated)

[api]
host = router.example.com
username = admin
password = securepassword
port = 8728
address_list = DNS_Filter
comment = Added by DNS Proxy
```