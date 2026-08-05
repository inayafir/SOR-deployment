"""One-command build script for the CHSS SOR intranet application.

Produces ``release/Application/`` containing ``Application.exe``, the runtime
folders and the deployment documentation.

Usage
-----
    python build.py

or double-click ``build.bat``.

The build machine needs Python + pip + internet (to install dependencies and
PyInstaller). The built package itself needs none of these.
"""

import http.cookiejar
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from importlib.util import find_spec

ROOT = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(ROOT, "sor_app.spec")
DIST_EXE = os.path.join(ROOT, "dist", "Application.exe")
RELEASE_DIR = os.path.join(ROOT, "release", "Application")
RUNTIME_FOLDERS = ("database", "uploads", "exports", "backup", "logs", "config")
DOCS = ("DEPLOY.md", "README.md")
MIN_EXE_SIZE = 5 * 1024 * 1024
SMOKE_PORT = 8099
SMOKE_TIMEOUT = 90


def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.check_call(cmd)


def ensure_runtime_deps():
    """Install runtime requirements (Flask, Werkzeug, Waitress) if missing."""
    if not (find_spec("flask") and find_spec("waitress")):
        run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def ensure_pyinstaller():
    if find_spec("PyInstaller") is None:
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def clean():
    for name in ("build", "dist", "release"):
        shutil.rmtree(os.path.join(ROOT, name), ignore_errors=True)


def build_exe():
    run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", SPEC])


def assemble_release():
    os.makedirs(RELEASE_DIR, exist_ok=True)
    shutil.copy2(DIST_EXE, os.path.join(RELEASE_DIR, "Application.exe"))
    for folder in RUNTIME_FOLDERS:
        os.makedirs(os.path.join(RELEASE_DIR, folder), exist_ok=True)
    for doc in DOCS:
        src = os.path.join(ROOT, doc)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(RELEASE_DIR, doc))


def http_get(url, opener, data=None):
    """GET or POST (with url-encoded body) and return (status, body, url)."""
    req = urllib.request.Request(url, data=data)
    with opener.open(req, timeout=5) as resp:
        return resp.status, resp.read().decode("utf-8", "replace"), resp.geturl()


def verify_app(tmp):
    """Exercise the running frozen exe: login, search page, data API, DB file."""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    base = f"http://127.0.0.1:{SMOKE_PORT}"

    status, _, _ = http_get(f"{base}/login", opener)
    assert status == 200, f"/login returned {status}"

    body = "username=admin&password=admin123"
    status, _, url = http_get(
        f"{base}/login", opener, data=body.encode("ascii"),
    )
    assert url.endswith("/search"), f"login did not redirect to /search (got {url})"

    status, html, _ = http_get(f"{base}/search", opener)
    assert status == 200 and "SOR Code" in html, "search page did not render"

    status, payload, _ = http_get(
        f"{base}/api/search?q=catheter", opener,
    )
    assert status == 200 and '"total"' in payload, "search API returned no data"

    db_path = os.path.join(tmp, "database", "sor.db")
    assert os.path.exists(db_path), f"runtime DB not created at {db_path}"
    return db_path


def kill_tree(pid):
    """Force-kill a process and all its children (Windows taskkill)."""
    if not pid:
        return
    subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        capture_output=True, check=False,
    )


def smoke_test():
    """Launch the exe in an isolated temp folder and exercise it."""
    with socket.socket() as s:
        if s.connect_ex(("127.0.0.1", SMOKE_PORT)) == 0:
            print(
                f"FAIL: port {SMOKE_PORT} is already in use. A previous "
                f"Application.exe may still be running — end it in Task "
                f"Manager and re-run.",
            )
            sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="sor_smoke_")
    exe = os.path.join(tmp, "Application.exe")
    shutil.copy2(DIST_EXE, exe)

    env = dict(os.environ)
    env["SOR_PORT"] = str(SMOKE_PORT)
    env["SOR_HOST"] = "127.0.0.1"

    proc = subprocess.Popen(
        [exe], cwd=tmp, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + SMOKE_TIMEOUT
        last_error = "not started"
        while time.time() < deadline:
            if proc.poll() is not None:
                print(f"FAIL: exe exited early with code {proc.returncode}")
                sys.exit(1)
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{SMOKE_PORT}/login", timeout=2,
                ) as resp:
                    if resp.status == 200:
                        break
            except Exception as exc:  # noqa: BLE001 - server may still be starting
                last_error = exc
            time.sleep(2)
        else:
            print(f"FAIL: smoke test timed out — {last_error}")
            sys.exit(1)

        try:
            db_path = verify_app(tmp)
        except Exception as exc:  # noqa: BLE001 - report the real failure
            print(f"FAIL: smoke test verification error — {exc}")
            sys.exit(1)
        print(
            f"Smoke test OK: exe served login/search/API on "
            f"127.0.0.1:{SMOKE_PORT} and seeded {db_path}",
        )
    finally:
        kill_tree(proc.pid)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    os.chdir(ROOT)
    print("== CHSS SOR build ==")
    ensure_runtime_deps()
    ensure_pyinstaller()
    clean()
    build_exe()

    if not os.path.exists(DIST_EXE):
        print("FAIL: Application.exe was not produced.")
        sys.exit(1)
    size = os.path.getsize(DIST_EXE)
    if size < MIN_EXE_SIZE:
        print(f"WARN: Application.exe is only {size:,} bytes — unexpectedly small.")
    print(f"Built Application.exe ({size:,} bytes)")

    assemble_release()
    smoke_test()

    print("\nBUILD SUCCEEDED")
    print("Deployable package:", RELEASE_DIR)
    print("Copy the whole 'Application' folder to the server PC and run "
          "Application.exe.")


if __name__ == "__main__":
    main()
