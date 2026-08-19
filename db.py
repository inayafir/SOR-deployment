"""Database helpers for the SOR search application.

The database is a single shared SQLite file stored under the runtime
``database/`` folder (next to the executable in production). SQLite is
opened in WAL mode with a busy timeout so multiple intranet users can search
concurrently while writes remain atomic. Every modification is performed
inside a transaction (see :func:`get_db`).
"""

import csv
import logging
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from categories import classify_category, sort_categories
from paths import get_backup_dir, get_db_path, get_rollback_path, resource_path

logger = logging.getLogger("sor.db")

DB_PATH = get_db_path()
SOR_CSV_PATH = resource_path("chss_sor_2023.csv")
ROLLBACK_PATH = get_rollback_path()

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_USER_USERNAME = "user"
DEFAULT_USER_PASSWORD = "user123"

PER_PAGE = 20
BACKUP_KEEP = 14

# CSV columns are positional to avoid encoding issues with the header names.
CODE_INDEX = 0   # Sl. No.
NAME_INDEX = 1   # Service Name / Name of Treatment/Procedure/Investigation
RATE_INDEX = 2   # CHSS SOR New Rate (₹)


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("Database operation failed; transaction rolled back.")
        raise
    finally:
        conn.close()


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def backup_database():
    """Take a consistent snapshot of the database into ``backup/``.

    Uses SQLite's online backup API, which captures a stable snapshot even
    while other connections are reading or writing (WAL). Called once at
    startup. Old backups beyond ``BACKUP_KEEP`` are pruned.
    """
    if not os.path.exists(DB_PATH):
        return None
    backup_dir = get_backup_dir()
    os.makedirs(backup_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(backup_dir, f"sor_{stamp}.db")

    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(dest)
    try:
        with dst:
            src.backup(dst)
    finally:
        src.close()
        dst.close()

    backups = sorted(
        f for f in os.listdir(backup_dir) if f.startswith("sor_") and f.endswith(".db")
    )
    for stale in backups[:-BACKUP_KEEP]:
        try:
            os.remove(os.path.join(backup_dir, stale))
        except OSError:
            pass
    logger.info("Database backup created: %s", os.path.basename(dest))
    return dest


def init_db():
    """Create tables if needed, seed default users, and seed SOR data on a
    fresh database (i.e. when the sor_items table is created for the first
    time)."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        fresh = (
            conn.execute(
                "SELECT COUNT(*) FROM sqlite_master "
                "WHERE type = 'table' AND name = 'sor_items'"
            ).fetchone()[0]
            == 0
        )
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
            );
            CREATE TABLE IF NOT EXISTS sor_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sor_code TEXT UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_sor_items_category
                ON sor_items(category);
            CREATE INDEX IF NOT EXISTS idx_sor_items_name
                ON sor_items(name);
            """
        )
        _seed_users(conn)
        if fresh:
            _seed_sor_items(conn)
        _migrate_sor_code_nullable(conn)


def _migrate_sor_code_nullable(conn):
    """Make the ``sor_code`` column nullable on databases created before the
    code became optional. Idempotent; a no-op on current schemas.

    PRAGMA table_info rows are ``(cid, name, type, notnull, dflt_value, pk)``;
    tuple indices are used so the check works with any connection factory.
    """
    code_not_null = False
    for col in conn.execute("PRAGMA table_info(sor_items)").fetchall():
        if col[1] == "sor_code":
            code_not_null = bool(col[3])
            break
    if not code_not_null:
        return
    conn.execute("DROP TABLE IF EXISTS sor_items_old")
    conn.execute("ALTER TABLE sor_items RENAME TO sor_items_old")
    conn.execute(
        """CREATE TABLE sor_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sor_code TEXT UNIQUE,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )
    conn.execute(
        """INSERT INTO sor_items
           (id, sor_code, name, category, price, created_at, updated_at)
           SELECT id, sor_code, name, category, price, created_at, updated_at
           FROM sor_items_old"""
    )
    conn.execute("DROP TABLE sor_items_old")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sor_items_category ON sor_items(category)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sor_items_name ON sor_items(name)"
    )
    logger.info("Migrated sor_items.sor_code to nullable")


def _seed_users(conn):
    defaults = [
        (DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, "admin"),
        (DEFAULT_USER_USERNAME, DEFAULT_USER_PASSWORD, "user"),
    ]
    for username, password, role in defaults:
        exists = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) "
                "VALUES (?, ?, ?)",
                (username, generate_password_hash(password), role),
            )


def _parse_rate(value):
    """Return the first numeric price found in a rate cell, or None when the
    cell is empty or contains no number.

    Handles multi-value and annotated cells such as ``'1000 | 1500 | 2000'``
    (returns ``1000``), ``'2300 | [per | sitting]'`` (returns ``2300``), and
    ``'At actuals'`` (returns ``None``)."""
    text = (value or "").strip().replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group())


def _seed_sor_items(conn):
    if not os.path.exists(SOR_CSV_PATH):
        return
    now = _now()
    inserted = 0
    with open(SOR_CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return
        for fields in reader:
            if len(fields) < 3:
                continue
            sor_code = fields[CODE_INDEX].strip()
            name = fields[NAME_INDEX].strip()
            if not sor_code or not name:
                continue
            price = _parse_rate(fields[RATE_INDEX])
            category = classify_category(name, sor_code)
            conn.execute(
                """INSERT INTO sor_items
                   (sor_code, name, category, price, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (sor_code, name, category, price, now, now),
            )
            inserted += 1
    print(f"Seeded {inserted} SOR items from {os.path.basename(SOR_CSV_PATH)}")


def authenticate_user(username, password):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role FROM users "
            "WHERE username = ?",
            (username.strip(),),
        ).fetchone()
        if row and check_password_hash(row["password_hash"], password):
            return {
                "id": row["id"],
                "username": row["username"],
                "role": row["role"],
            }
    return None


def _normalize_field(field):
    field = (field or "both").strip().lower()
    return field if field in ("name", "code", "both") else "both"


def search_sor_items(q=None, category=None, field=None, page=1, per_page=PER_PAGE):
    """Search SOR items by name and/or code with an optional category filter.

    Returns ``(items, total)`` where items is the page slice ordered by
    SOR code. ``q`` is matched partially and case-insensitively. ``field``
    restricts matching to ``"name"``, ``"code"``, or ``"both"`` (default).
    """
    q = (q or "").strip()
    category = (category or "").strip()
    field = _normalize_field(field)
    where = []
    params = []
    if q:
        like = f"%{q}%"
        if field == "name":
            where.append("name LIKE ?")
            params.append(like)
        elif field == "code":
            where.append("sor_code LIKE ?")
            params.append(like)
        else:
            where.append("(name LIKE ? OR sor_code LIKE ?)")
            params.extend([like, like])
    if category:
        where.append("category = ?")
        params.append(category)
    clause = ("WHERE " + " AND ".join(where)) if where else ""

    with get_db() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM sor_items {clause}", params
        ).fetchone()[0]
        page = max(1, int(page))
        offset = (page - 1) * per_page
        rows = conn.execute(
            f"""SELECT * FROM sor_items {clause}
                ORDER BY (sor_code IS NULL), CAST(sor_code AS INTEGER), sor_code
                LIMIT ? OFFSET ?""",
            params + [per_page, offset],
        ).fetchall()
        return [dict(r) for r in rows], total


def get_sor_item(sor_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sor_items WHERE id = ?", (sor_id,)
        ).fetchone()
        return dict(row) if row else None


def _clean_code(sor_code):
    """Normalise an optional SOR code: blank becomes None, otherwise strip."""
    if sor_code is None:
        return None
    code = str(sor_code).strip()
    return code or None


def _clean_price(price):
    if price is None:
        return None
    return float(price)


def get_sor_item_by_code(sor_code, exclude_id=None):
    code = _clean_code(sor_code)
    if not code:
        return None
    with get_db() as conn:
        if exclude_id is None:
            row = conn.execute(
                "SELECT * FROM sor_items WHERE sor_code = ?",
                (code,),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM sor_items WHERE sor_code = ? AND id != ?",
                (code, exclude_id),
            ).fetchone()
        return dict(row) if row else None


def create_sor_item(sor_code, name, category, price):
    now = _now()
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO sor_items
               (sor_code, name, category, price, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (_clean_code(sor_code), name.strip(), category.strip(),
             _clean_price(price), now, now),
        )
        return cursor.lastrowid


def update_sor_item(sor_id, sor_code, name, category, price):
    with get_db() as conn:
        conn.execute(
            """UPDATE sor_items
               SET sor_code = ?, name = ?, category = ?, price = ?,
                   updated_at = ?
               WHERE id = ?""",
            (_clean_code(sor_code), name.strip(), category.strip(),
             _clean_price(price), _now(), sor_id),
        )


def replace_sor_items(items):
    """Replace the entire SOR dataset with ``items`` in a single transaction.

    ``items`` is a list of dicts with keys ``sor_code``, ``name``,
    ``category``, ``price``. If any insert fails the whole transaction is
    rolled back so the live database is never left half-replaced.
    """
    now = _now()
    rows = [
        (_clean_code(it["sor_code"]), it["name"].strip(),
         it["category"].strip(), _clean_price(it["price"]), now, now)
        for it in items
    ]
    with get_db() as conn:
        conn.execute("DELETE FROM sor_items")
        conn.executemany(
            """INSERT INTO sor_items
               (sor_code, name, category, price, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            rows,
        )
    logger.info("Replaced SOR dataset with %d items", len(items))


def list_all_sor_items():
    """Return every SOR item ordered by code for export."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT sor_code, name, category, price FROM sor_items
               ORDER BY (sor_code IS NULL), CAST(sor_code AS INTEGER), sor_code"""
        ).fetchall()
        return [dict(r) for r in rows]


def create_rollback():
    """Snapshot the live database into the single rollback file.

    Uses SQLite's online backup API so the snapshot is consistent even while
    other requests are reading or writing. Only one rollback snapshot is kept;
    the next import overwrites it.
    """
    if not os.path.exists(DB_PATH):
        return False
    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(ROLLBACK_PATH)
    try:
        with dst:
            src.backup(dst)
    finally:
        src.close()
        dst.close()
    logger.info("Rollback snapshot created: %s", ROLLBACK_PATH)
    return True


def has_rollback():
    return os.path.exists(ROLLBACK_PATH)


def restore_rollback():
    """Restore the live database from the rollback snapshot.

    Returns True when a snapshot existed and was restored. Uses the online
    backup API so restoration is atomic and safe under WAL mode.
    """
    if not os.path.exists(ROLLBACK_PATH):
        return False
    src = sqlite3.connect(ROLLBACK_PATH)
    dst = sqlite3.connect(DB_PATH)
    try:
        with dst:
            src.backup(dst)
    finally:
        src.close()
        dst.close()
    logger.info("Database restored from rollback snapshot")
    return True


def delete_sor_item(sor_id):
    with get_db() as conn:
        conn.execute("DELETE FROM sor_items WHERE id = ?", (sor_id,))


def list_categories():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM sor_items"
        ).fetchall()
        cats = [r["category"] for r in rows]
    from categories import DEFAULT_CATEGORY
    if DEFAULT_CATEGORY not in cats:
        cats.append(DEFAULT_CATEGORY)
    return sort_categories(cats)


def suggest_sor_items(q, field=None, limit=10):
    """Return ranked suggestions for the autocomplete dropdown.

    Matches are restricted to ``field`` (``"name"``, ``"code"``, or
    ``"both"``). Exact code matches rank first, then code-prefix, then
    name-prefix, then substring matches. All matching is case-insensitive.
    """
    q = (q or "").strip()
    if not q:
        return []
    field = _normalize_field(field)
    contains = f"%{q}%"
    prefix = f"{q}%"

    if field == "name":
        match = "name LIKE ?"
        order = "CASE WHEN name LIKE ? THEN 0 ELSE 1 END"
        params = [contains, prefix]
    elif field == "code":
        match = "sor_code LIKE ?"
        order = (
            "CASE WHEN sor_code = ? THEN 0 "
            "WHEN sor_code LIKE ? THEN 1 ELSE 2 END"
        )
        params = [contains, q, prefix]
    else:
        match = "(name LIKE ? OR sor_code LIKE ?)"
        order = (
            "CASE WHEN sor_code = ? THEN 0 "
            "WHEN sor_code LIKE ? THEN 1 "
            "WHEN name LIKE ? THEN 2 ELSE 3 END"
        )
        params = [contains, contains, q, prefix, prefix]

    with get_db() as conn:
        rows = conn.execute(
            f"""SELECT id, sor_code, name, category, price
                FROM sor_items
                WHERE {match}
                ORDER BY {order}, (sor_code IS NULL), CAST(sor_code AS INTEGER)
                LIMIT ?""",
            params + [limit],
        ).fetchall()
        return [dict(r) for r in rows]
