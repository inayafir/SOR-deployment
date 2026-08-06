"""CHSS Schedule of Rates (SOR) — Search & Management Application.

Production deployment notes
---------------------------
* Served by the Waitress WSGI server — never the Flask development server.
* Binds to ``0.0.0.0`` by default so every PC on the intranet can reach it at
  ``http://SERVER_IP:PORT``.
* Runtime data (database, logs, config, uploads, exports, backups) lives next
  to the executable and persists across restarts. See ``paths.py``.
* Host, port and thread count are configurable via ``config/config.ini`` or
  the ``SOR_HOST`` / ``SOR_PORT`` / ``SOR_THREADS`` environment variables.
* All unexpected exceptions are logged and turned into friendly error pages;
  they never terminate the server.
"""

import io
import logging
import math
import os
import re
import secrets
import sys
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

from flask import (
    Flask, abort, flash, jsonify, redirect, render_template, request,
    send_file, session, url_for,
)
from werkzeug.exceptions import HTTPException

import config as app_config
import db
import excel
import paths

# ---------------------------------------------------------------------------
# Logging (rotating file + console)
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5
LOGGER_NAME = "sor"

_logging_configured = False


def setup_logging():
    """Configure rotating file logging plus a console handler (idempotent)."""
    global _logging_configured
    if _logging_configured:
        return logging.getLogger(LOGGER_NAME)
    _logging_configured = True

    paths.ensure_runtime_dirs()
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(
        os.path.join(paths.get_logs_dir(), "app.log"),
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    return logging.getLogger(LOGGER_NAME)


logger = setup_logging()

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
CONFIG = app_config.load_config()

app = Flask(
    __name__,
    template_folder=paths.resource_path("templates"),
    static_folder=paths.resource_path("static"),
)
app.config["PROPAGATE_EXCEPTIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
app.secret_key = CONFIG["security"]["secret_key"]

SERVER_CONFIG = CONFIG["server"]


# ---------------------------------------------------------------------------
# CSRF helpers
# ---------------------------------------------------------------------------
def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def csrf_protect(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return f(*args, **kwargs)
        token = session.get("_csrf_token")
        submitted = request.form.get("_csrf_token")
        if not token or not submitted or not secrets.compare_digest(token, submitted):
            abort(400, "Invalid or missing CSRF token.")
        return f(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def login_required(role=None):
    """Require an authenticated user, optionally restricted to ``role``."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def api_login_required(f):
    """Require login for JSON endpoints; returns 401 instead of redirecting."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapped


def current_user():
    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "role": session.get("role"),
    }


# ---------------------------------------------------------------------------
# Login throttling (brute-force protection)
# ---------------------------------------------------------------------------
_LOGIN_MAX_ATTEMPTS = 5
_LOGIN_LOCK_SECONDS = 15 * 60
_LOGIN_MAX_KEYS = 1000
_login_failures = {}


def _login_key(username, ip):
    return f"{username}|{ip}"


def _prune_login_failures():
    if len(_login_failures) <= _LOGIN_MAX_KEYS:
        return
    cutoff = time.time() - _LOGIN_LOCK_SECONDS
    for key in [k for k, stamps in _login_failures.items()
                if not stamps or stamps[-1] <= cutoff]:
        _login_failures.pop(key, None)


def _login_locked(username, ip):
    key = _login_key(username, ip)
    cutoff = time.time() - _LOGIN_LOCK_SECONDS
    stamps = [t for t in _login_failures.get(key, []) if t > cutoff]
    _login_failures[key] = stamps
    return len(stamps) >= _LOGIN_MAX_ATTEMPTS


def _register_login_failure(username, ip):
    _prune_login_failures()
    key = _login_key(username, ip)
    _login_failures.setdefault(key, []).append(time.time())


def _clear_login_failures(username, ip):
    _login_failures.pop(_login_key(username, ip), None)


# ---------------------------------------------------------------------------
# Audit logging for sensitive actions
# ---------------------------------------------------------------------------
def _audit(action, detail=""):
    actor = current_user().get("username") or "anonymous"
    logger.info("AUDIT user=%s action=%s %s", actor, action, detail)


@app.context_processor
def inject_globals():
    return {
        "csrf_token": generate_csrf_token(),
        "current_user": current_user(),
        "format_price": format_price,
    }


def format_price(value):
    if value is None:
        return ""
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}"


def _parse_page():
    try:
        return max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        return 1


def _search_kwargs():
    return {
        "q": request.args.get("q", "").strip(),
        "category": request.args.get("category", "").strip(),
        "field": request.args.get("field", "").strip(),
        "page": _parse_page(),
    }


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("search"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        ip = request.remote_addr or "unknown"

        if _login_locked(username, ip):
            logger.warning(
                "Login blocked for user=%s from %s (too many attempts)",
                username, ip,
            )
            flash(
                "Too many failed attempts. Please try again in 15 minutes.",
                "danger",
            )
            return render_template("login.html"), 429

        user = db.authenticate_user(username, password)
        if user:
            _clear_login_failures(username, ip)
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            logger.info(
                "Login success user=%s from %s", user["username"], ip,
            )
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for("search"))
        _register_login_failure(username, ip)
        logger.warning(
            "Login failed user=%s from %s", username, ip,
        )
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@csrf_protect
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# SOR search (User and Admin)
# ---------------------------------------------------------------------------
@app.route("/search")
@login_required()
def search():
    kwargs = _search_kwargs()
    items, total = db.search_sor_items(**kwargs)
    per_page = db.PER_PAGE
    total_pages = max(1, math.ceil(total / per_page))
    return render_template(
        "sor_search.html",
        items=items,
        total=total,
        page=kwargs["page"],
        total_pages=total_pages,
        q=kwargs["q"],
        category=kwargs["category"],
        field=kwargs["field"],
        categories=db.list_categories(),
        per_page=per_page,
    )


# ---------------------------------------------------------------------------
# Search API (used by the dynamic search UI)
# ---------------------------------------------------------------------------
@app.route("/api/search")
@api_login_required
def api_search():
    kwargs = _search_kwargs()
    items, total = db.search_sor_items(**kwargs)
    per_page = db.PER_PAGE
    return jsonify({
        "q": kwargs["q"],
        "category": kwargs["category"],
        "field": kwargs["field"],
        "page": kwargs["page"],
        "per_page": per_page,
        "total": total,
        "total_pages": max(1, math.ceil(total / per_page)),
        "items": items,
    })


@app.route("/api/suggest")
@api_login_required
def api_suggest():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"items": []})
    return jsonify({
        "items": db.suggest_sor_items(
            q, field=request.args.get("field", "").strip()
        )
    })


# ---------------------------------------------------------------------------
# SOR management (Admin only)
# ---------------------------------------------------------------------------
@app.route("/manage")
@login_required(role="admin")
def manage():
    kwargs = _search_kwargs()
    items, total = db.search_sor_items(**kwargs)
    per_page = db.PER_PAGE
    total_pages = max(1, math.ceil(total / per_page))
    return render_template(
        "sor_manage.html",
        items=items,
        total=total,
        page=kwargs["page"],
        total_pages=total_pages,
        q=kwargs["q"],
        category=kwargs["category"],
        field=kwargs["field"],
        categories=db.list_categories(),
        per_page=per_page,
        rollback_available=db.has_rollback(),
    )


# ---------------------------------------------------------------------------
# Bulk database import / export / rollback (Admin only)
# ---------------------------------------------------------------------------
@app.route("/manage/export")
@login_required(role="admin")
def manage_export():
    data = excel.export_to_bytes()
    _audit("export")
    return send_file(
        io.BytesIO(data),
        as_attachment=True,
        download_name=excel.default_filename(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/manage/import", methods=["POST"])
@login_required(role="admin")
@csrf_protect
def manage_import():
    file = request.files.get("excel")
    if file is None or not file.filename:
        flash("Please choose an Excel file to upload.", "danger")
        return redirect(url_for("manage"))
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        flash("Please upload an .xlsx or .xls file.", "danger")
        return redirect(url_for("manage"))

    data = file.stream.read()
    try:
        items = excel.parse_import_rows(data)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("manage"))

    db.create_rollback()
    db.replace_sor_items(items)
    _audit("import", f"rows={len(items)}")
    flash(
        f"Database replaced with {len(items)} items. The previous database "
        "is kept for rollback.",
        "success",
    )
    return redirect(url_for("manage"))


@app.route("/manage/rollback", methods=["POST"])
@login_required(role="admin")
@csrf_protect
def manage_rollback():
    if not db.has_rollback():
        flash("No previous database is available to roll back to.", "warning")
        return redirect(url_for("manage"))
    db.restore_rollback()
    _audit("rollback")
    flash("Database restored to the previous version.", "success")
    return redirect(url_for("manage"))


def _validate_sor_form(exclude_id=None):
    """Validate the create/edit form. Returns (errors, cleaned_values)."""
    sor_code = request.form.get("sor_code", "").strip()
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price_str = request.form.get("price", "").strip()

    errors = []
    if sor_code and not re.fullmatch(r"[A-Za-z0-9]+", sor_code):
        errors.append("SOR code must be alphanumeric (letters and digits only).")
    if sor_code and db.get_sor_item_by_code(sor_code, exclude_id=exclude_id):
        errors.append(f"SOR code '{sor_code}' already exists.")
    if not name:
        errors.append("Service name is required.")
    if category not in db.list_categories():
        errors.append("Please choose a valid category.")
    price = None
    try:
        price = float(price_str.replace(",", ""))
        if not math.isfinite(price) or price < 0:
            errors.append("Price must be a positive number.")
    except (TypeError, ValueError):
        errors.append("Price must be a valid number.")
    return errors, {
        "sor_code": sor_code or None,
        "name": name,
        "category": category,
        "price": price,
    }


@app.route("/sor/new", methods=["GET", "POST"])
@login_required(role="admin")
@csrf_protect
def sor_new():
    if request.method == "POST":
        errors, values = _validate_sor_form()
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "sor_form.html",
                item=None,
                form=request.form,
                categories=db.list_categories(),
            ), 400
        db.create_sor_item(
            values["sor_code"], values["name"],
            values["category"], values["price"],
        )
        _audit("create", f"sor_code={values['sor_code']!r}")
        flash("SOR item added.", "success")
        return redirect(url_for("manage"))

    return render_template(
        "sor_form.html",
        item=None,
        form={},
        categories=db.list_categories(),
    )


@app.route("/sor/<int:sor_id>/edit", methods=["GET", "POST"])
@login_required(role="admin")
@csrf_protect
def sor_edit(sor_id):
    item = db.get_sor_item(sor_id)
    if not item:
        abort(404)
    if request.method == "POST":
        errors, values = _validate_sor_form(exclude_id=sor_id)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "sor_form.html",
                item=item,
                form={**request.form, "id": sor_id},
                categories=db.list_categories(),
            ), 400
        db.update_sor_item(
            sor_id, values["sor_code"], values["name"],
            values["category"], values["price"],
        )
        _audit("update", f"sor_id={sor_id} sor_code={values['sor_code']!r}")
        flash("SOR item updated.", "success")
        return redirect(url_for("manage"))

    form = dict(item)
    if form.get("price") is None:
        form["price"] = ""
    return render_template(
        "sor_form.html",
        item=item,
        form=form,
        categories=db.list_categories(),
    )


@app.route("/sor/<int:sor_id>/delete", methods=["POST"])
@login_required(role="admin")
@csrf_protect
def sor_delete(sor_id):
    item = db.get_sor_item(sor_id)
    if not item:
        abort(404)
    db.delete_sor_item(sor_id)
    _audit("delete", f"sor_id={sor_id} sor_code={item['sor_code']!r}")
    flash(f"SOR item {item['sor_code']} deleted.", "info")
    return redirect(url_for("manage"))


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------
@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    return response


@app.after_request
def log_request(response):
    """Log failed requests so operational issues are visible in the logs."""
    if response.status_code >= 500:
        logger.error(
            "Request %s %s -> %s", request.method, request.path,
            response.status_code,
        )
    elif response.status_code >= 400:
        logger.warning(
            "Request %s %s -> %s", request.method, request.path,
            response.status_code,
        )
    return response


@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", code=400, message="Bad request."), 400


@app.errorhandler(403)
def forbidden(e):
    return render_template(
        "error.html", code=403,
        message="You do not have permission to view this page.",
    ), 403


@app.errorhandler(404)
def not_found(e):
    return render_template(
        "error.html", code=404,
        message="The page you are looking for was not found.",
    ), 404


@app.errorhandler(Exception)
def unhandled_exception(exc):
    """Last-resort handler: log everything and never crash the server."""
    if isinstance(exc, HTTPException):
        code = exc.code or 500
        message = exc.description or "The page could not be loaded."
    else:
        code = 500
        message = "Something went wrong on our end."
    logger.exception(
        "Unhandled exception while serving %s %s", request.method, request.path,
    )
    return render_template("error.html", code=code, message=message), code


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    setup_logging()
    paths.ensure_runtime_dirs()
    db.init_db()
    db.backup_database()

    host = SERVER_CONFIG["host"]
    port = SERVER_CONFIG["port"]
    threads = SERVER_CONFIG["threads"]

    logger.info(
        "Starting CHSS SOR server on %s:%s (threads=%s). "
        "Base dir: %s", host, port, threads, paths.BASE_DIR,
    )

    try:
        import waitress
        waitress.serve(
            app,
            host=host,
            port=port,
            threads=threads,
            ident="CHSS-SOR",
        )
    except KeyboardInterrupt:
        logger.info("Shutdown requested by operator (Ctrl+C).")
    except OSError as exc:
        logger.critical(
            "Could not start server on %s:%s — %s", host, port, exc,
        )
        print(f"ERROR: Could not start server on {host}:{port}. "
              f"Is the port already in use? ({exc})")
        sys.exit(1)
    finally:
        logger.info("Application stopped.")


if __name__ == "__main__":
    main()
