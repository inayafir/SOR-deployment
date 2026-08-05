"""Configuration loading and persistence.

Configuration lives in ``config/config.ini`` next to the executable. On the
deployment machine this file persists across restarts, so it is the single
source of truth for server settings. Environment variables always override
file values, which is useful for one-off changes without editing files.

Config sections:

``[server]``
    host    - interface to bind (default ``0.0.0.0`` for intranet access)
    port    - TCP port (default ``8080``)
    threads - Waitress worker threads (default ``8``)

``[security]``
    secret_key - session-signing key; generated automatically on first run so
                 sessions survive restarts.
"""

import configparser
import os
import secrets

from paths import ensure_runtime_dirs, get_config_path

_ENV_HOST = "SOR_HOST"
_ENV_PORT = "SOR_PORT"
_ENV_THREADS = "SOR_THREADS"
_ENV_SECRET = "SECRET_KEY"

_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 8080
_DEFAULT_THREADS = 8


def _default_secret_key():
    return secrets.token_hex(32)


def _as_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_config():
    """Load configuration, creating ``config/config.ini`` with defaults and a
    generated secret key on the first run."""
    ensure_runtime_dirs()
    path = get_config_path()

    parser = configparser.ConfigParser()
    if os.path.exists(path):
        parser.read(path, encoding="utf-8")
    else:
        parser["server"] = {
            "host": _DEFAULT_HOST,
            "port": str(_DEFAULT_PORT),
            "threads": str(_DEFAULT_THREADS),
        }
        parser["security"] = {"secret_key": _default_secret_key()}
        _save(parser, path)

    server = parser["server"] if parser.has_section("server") else {}
    security = parser["security"] if parser.has_section("security") else {}

    secret_key = os.environ.get(_ENV_SECRET) or server_get(security, "secret_key")
    if not secret_key:
        secret_key = _default_secret_key()
        if not parser.has_section("security"):
            parser.add_section("security")
        parser.set("security", "secret_key", secret_key)
        _save(parser, path)

    return {
        "server": {
            "host": os.environ.get(_ENV_HOST) or server_get(server, "host", _DEFAULT_HOST),
            "port": _as_int(
                os.environ.get(_ENV_PORT) or server_get(server, "port"),
                _DEFAULT_PORT,
            ),
            "threads": _as_int(
                os.environ.get(_ENV_THREADS) or server_get(server, "threads"),
                _DEFAULT_THREADS,
            ),
        },
        "security": {"secret_key": secret_key},
    }


def server_get(section, key, default=None):
    if not section or not section.get(key):
        return default
    return section.get(key)


def _save(parser, path):
    with open(path, "w", encoding="utf-8") as f:
        parser.write(f)
