"""Runtime paths and directory management.

The application can run from source (``python app.py``) or as a frozen
PyInstaller executable. In both cases:

* ``get_base_dir()`` is where runtime data (database, logs, config, uploads,
  exports, backups) lives. For the frozen application this is the folder
  containing the ``.exe`` so all data persists across restarts.
* ``get_resource_dir()`` is where bundled read-only resources (templates,
  static assets, the seed CSV) are unpacked by PyInstaller.

No module should build a runtime path from ``__file__``; it is not stable
under PyInstaller. Use this module instead.
"""

import os
import sys


def get_base_dir():
    """Directory that holds persistent runtime data (next to the exe)."""
    override = os.environ.get("SOR_DATA_DIR")
    if override:
        return os.path.abspath(override)
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir():
    """Directory containing bundled, read-only application resources.

    This is independent of the data directory: resources always come from the
    PyInstaller bundle (frozen) or the project folder (source), never from an
    overridden data location.
    """
    if getattr(sys, "frozen", False):
        bundle = getattr(sys, "_MEIPASS", None)
        if bundle:
            return bundle
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative):
    """Absolute path to a bundled resource (template, static file, CSV)."""
    return os.path.join(get_resource_dir(), relative)


BASE_DIR = get_base_dir()

# Folders created automatically next to the executable on startup.
RUNTIME_DIRS = ("database", "uploads", "exports", "backup", "logs", "config")


def runtime_path(relative):
    """Absolute path to a file under the persistent base directory."""
    return os.path.join(BASE_DIR, relative)


def get_db_path():
    return runtime_path(os.path.join("database", "sor.db"))


def get_config_path():
    return runtime_path(os.path.join("config", "config.ini"))


def get_logs_dir():
    return runtime_path("logs")


def get_backup_dir():
    return runtime_path("backup")


def get_rollback_path():
    """Single-file snapshot of the database state immediately before the last
    bulk import. Restoring it rolls the database back one step."""
    return runtime_path(os.path.join("database", "sor_rollback.db"))


def ensure_runtime_dirs():
    """Create every runtime directory if it does not exist. Never fails."""
    for name in RUNTIME_DIRS:
        os.makedirs(runtime_path(name), exist_ok=True)
    return BASE_DIR
