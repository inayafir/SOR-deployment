# CHSS Schedule of Rates (SOR) — Search & Management

A lightweight, two-role web application to search the official CHSS Schedule
of Rates and manage its entries. Built to run as a standalone **offline
intranet application** (single server PC, any number of browser clients).

## Features

- **Search & Filter**: partial, case-insensitive search by service name or
  SOR code (selectable), plus a category filter, with pagination (20 items
  per page) and live Google-style autocomplete.
- **Roles**:
  - **User** — login and search/filter the SOR (read-only).
  - **Admin** — everything a User can do, plus add / edit / delete SOR items.
- **Shared single database**: all users read and write the one SQLite file
  on the server; changes appear for every user immediately.
- **Security**: salted password hashes (Werkzeug), session-based auth, RBAC,
  CSRF protection on all state-changing requests, friendly 400/403/404/500
  pages.
- **Categories**: derived automatically from the CSV at seed time via
  `categories.py` (the source CSV has no category column).
- **Production ready**: Waitress WSGI server, WAL-mode SQLite with busy
  timeout, rotating logs, configurable port, PyInstaller packaging — no
  Python required on the deployment machine.

## Tech Stack

| Layer    | Technology                     |
|----------|--------------------------------|
| Frontend | HTML, CSS, Vanilla JS          |
| Backend  | Python Flask + Waitress (WSGI) |
| Database | SQLite (WAL mode)              |
| Packaging| PyInstaller (one-file .exe)    |
| Data     | `chss_sor_2023.csv`            |

## Project Structure

```
URSC-accts-sor/
├── app.py               # Flask application (routes, auth, CSRF, RBAC)
├── db.py                # Database helpers, CSV seeding, search (WAL)
├── categories.py        # Keyword-based category classifier
├── paths.py             # Runtime base-dir resolution (source vs frozen)
├── config.py            # config/config.ini + environment overrides
├── chss_sor_2023.csv    # Official Schedule of Rates (seeded once)
├── sor_app.spec         # PyInstaller specification
├── build.py / build.bat # One-command build script
├── DEPLOY.md            # Non-programmer deployment guide
├── requirements.txt
├── README.md
├── templates/           # base, login, sor_search, sor_manage, sor_form,
│                        # error, _pagination
├── static/
│   ├── css/style.css
│   └── js/common.js
└── runtime (auto-created next to the app):
    ├── database/        # SQLite database: sor.db
    ├── config/          # config.ini (host, port, threads, secret key)
    ├── logs/            # app.log (rotating)
    └── uploads/, exports/, backup/
        # backup/ holds automatic startup snapshots (newest 14 kept)
```

## Development (run from source)

```bash
pip install -r requirements.txt
python app.py
```

The database is created and seeded automatically on first run (2,154 SOR
items plus default accounts `admin/admin123` and `user/user123`).

## Configuration

Settings are read from `config/config.ini` (created on first run) and can be
overridden with environment variables:

| Setting           | Config file key      | Env var       | Default    |
|-------------------|----------------------|---------------|------------|
| Bind address      | `server.host`        | `SOR_HOST`    | `0.0.0.0`  |
| TCP port          | `server.port`        | `SOR_PORT`    | `8080`     |
| Worker threads    | `server.threads`     | `SOR_THREADS` | `8`        |
| Session secret    | `security.secret_key`| `SECRET_KEY`  | auto-generated |

## Building the standalone application

```bash
python build.py        # or double-click build.bat
```

The build produces `release/Application/` with `Application.exe`, runtime
folders and documentation, and runs a smoke test that the exe starts, logs in,
searches and seeds its database. See `DEPLOY.md` for full deployment
instructions.

## Default Credentials

| Role  | Username | Password   |
|-------|----------|------------|
| Admin | `admin`  | `admin123` |
| User  | `user`   | `user123`  |

**Change these before real deployment** (see `DEPLOY.md` §13).

## Usage

- **Search** (`/search`, any role): type a term, choose Name / SOR Code /
  Both, optionally filter by category; results and autocomplete update live.
- **Manage** (`/manage`, admin only): same search UI plus **Edit** /
  **Delete** actions per row and an **Add SOR Item** button.
- SOR codes must be unique; the service name is a required free-text field;
  price is a numeric amount (thousands separators allowed).

## Notes

- Fully offline; no external APIs or cloud services.
- Seeding happens only on a fresh database; restarting or deleting entries
  never re-imports data.
- On every start the database is snapshotted into `backup/` (newest 14 kept)
  so data can be restored even after accidental damage.
