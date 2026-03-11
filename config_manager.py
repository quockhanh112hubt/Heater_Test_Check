"""
Config Manager Module
Quản lý cấu hình từ file config.json
"""
import json
import os
from typing import Dict, Any

CONFIG_FILE = "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "update": {
        "program_directory": "C:\\Heater_Test_Check",
        "ftp_server": "10.62.102.5",
        "ftp_username": "update",
        "ftp_password": "update",
        "update_path": "/KhanhDQ/Update_Program/Heater_Test_Check/"
    },
    "database": {
        "sql_server": {
            "driver": "ODBC Driver 17 for SQL Server",
            "server": "10.162.200.32",
            "port": "1433",
            "database": "ITMV_KTNG_DB",
            "username": "ITMV_KTNG",
            "password": "!itm@semi!12"
        },
        "oracle": {
            "host": "10.162.200.20",
            "port": "1521",
            "service_name": "ITMVPACKMES",
            "username": "mighty",
            "password": "mighty"
        }
    }
}


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        else:
            # Create default config if not exists
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to config.json"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get_update_config() -> Dict[str, str]:
    """Get update configuration"""
    config = load_config()
    return config.get('update', DEFAULT_CONFIG['update'])


def get_ftp_base_url() -> str:
    """Build and return FTP base URL from config"""
    update_config = get_update_config()
    server = update_config.get('ftp_server', '10.62.102.5')
    username = update_config.get('ftp_username', 'update')
    password = update_config.get('ftp_password', 'update')
    path = update_config.get('update_path', '/KhanhDQ/Update_Program/Heater_Test_Check/')
    
    return f"ftp://{username}:{password}@{server}{path}"


def get_version_url() -> str:
    """Build and return version.txt URL from config"""
    base_url = get_ftp_base_url()
    return f"{base_url}version.txt"


def get_sql_server_config() -> Dict[str, str]:
    """Get SQL Server configuration"""
    config = load_config()
    return config.get('database', {}).get('sql_server', DEFAULT_CONFIG['database']['sql_server'])


def get_oracle_config() -> Dict[str, str]:
    """Get Oracle configuration"""
    config = load_config()
    return config.get('database', {}).get('oracle', DEFAULT_CONFIG['database']['oracle'])


def get_sql_connection_string() -> str:
    """Get SQL Server connection string"""
    sql_config = get_sql_server_config()
    return (
        f"DRIVER={{{sql_config['driver']}}};"
        f"SERVER={sql_config['server']},{sql_config['port']};"
        f"DATABASE={sql_config['database']};"
        f"UID={sql_config['username']};"
        f"PWD={sql_config['password']};"
    )


def get_oracle_dsn() -> str:
    """Get Oracle DSN connection string"""
    oracle_config = get_oracle_config()
    return (
        f"(DESCRIPTION="
        f"(LOAD_BALANCE=yes)"
        f"(ADDRESS=(PROTOCOL=TCP)(HOST={oracle_config['host']})(PORT={oracle_config['port']}))"
        f"(ADDRESS=(PROTOCOL=TCP)(HOST={oracle_config['host']})(PORT={oracle_config['port']}))"
        f"(CONNECT_DATA=(SERVICE_NAME={oracle_config['service_name']})"
        f"(FAILOVER_MODE=(TYPE=SELECT)(METHOD=BASIC))))"
    )


def get_oracle_connection_params() -> Dict[str, str]:
    """Get Oracle connection parameters"""
    oracle_config = get_oracle_config()
    return {
        'user': oracle_config['username'],
        'password': oracle_config['password'],
        'dsn': get_oracle_dsn()
    }
