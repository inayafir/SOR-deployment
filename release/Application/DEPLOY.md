# Deployment Guide — CHSS Schedule of Rates (SOR)

This guide explains how to put the SOR application onto a department server
PC and how users on the intranet access it. **No programming skills are
required.** Everything is done with folders, a file copy, and one
double-click.

---

## 1. What you are deploying

The deliverable is a folder called `Application`:

```
Application/
    Application.exe     <- the server application (double-click to start)
    database/           <- the shared database (created on first run)
    uploads/            <- (reserved) uploaded files
    exports/            <- (reserved) exported files
    backup/             <- (reserved) backups
    logs/               <- runtime logs (app.log, rotates automatically)
    config/             <- settings (config.ini, created on first run)
    DEPLOY.md           <- this document
    README.md
```

`Application.exe` contains Python, all libraries, web pages and the data
file **inside itself**. The deployment machine does not need Python, pip,
Git, the internet, or anything else installed.

All data lives in the folders **next to** the exe, so closing or restarting
the application never deletes anything.

---

## 2. Requirements

### Server PC (hosts the application)

| Item        | Requirement                                        |
|-------------|----------------------------------------------------|
| Operating system | Windows 10 / 11 (64-bit), or Windows Server 2016+ |
| Memory      | 512 MB RAM or more                                 |
| Disk        | 100 MB free space                                  |
| Network     | Connected to the department intranet (LAN)         |
| Internet    | **Not required** after installation                |

The server PC should be on all day. It does not need a monitor, but the
application must be started on it (or set to start automatically — see
section 11).

### Client PCs (everyone else)

Any PC on the intranet with a modern web browser (Chrome, Edge, Firefox).
Nothing is installed on client PCs.

---

## 3. Building the release package

Do this once on any Windows PC that has **Python 3.8+** installed.

1. Open a command prompt in the project folder.
2. Run:

   ```
   python build.py
   ```

   (or double-click `build.bat`).

The script installs the required libraries, builds `Application.exe`,
assembles the `release\Application` folder, and automatically tests that the
executable starts and serves the login page.

When it finishes you will see:

```
BUILD SUCCEEDED
Deployable package: ...\release\Application
```

---

## 4. First-time deployment onto the server

1. **Copy the `Application` folder** (from `release\`) to the server PC,
   e.g. to `C:\SOR\Application`. Copy the whole folder, not just the exe.
2. Double-click **`Application.exe`** on the server PC.
3. A black console window opens and shows a line like:

   ```
   Starting CHSS SOR server on 0.0.0.0:8080 ...
   ```

   Leave this window open — it is the server.
4. On the server PC itself, open a browser and go to:

   ```
   http://localhost:8080
   ```

   If the login page appears, the server is working.

> The `database`, `config` and `logs` folders are created automatically the
> first time. On first run the database is filled with all 2,154 SOR entries
> from the official CSV (bundled inside the exe).

---

## 5. Choosing a port

The default port is **8080**. To change it:

**Option A — settings file (recommended).** After the first run, open
`config\config.ini` in Notepad and edit:

```
[server]
port = 8080
```

Save the file, stop the application (see section 12) and start it again.

**Option B — environment variable.** Start the exe from a command prompt:

```
set SOR_PORT=9000
Application.exe
```

> Do not use ports already taken by other software (common ones: 80, 443,
> 8000, 8080, 8081, 3000). If the port is in use the application prints a
> clear error and closes.

---

## 6. Finding the server's IP address

1. On the server PC, open a Command Prompt and type:

   ```
   ipconfig
   ```

2. Find the entry for the network adapter connected to the intranet. The
   **IPv4 Address** (for example `192.168.1.50`) is the server address.
3. Use this address everywhere below instead of `192.168.1.50`.

---

## 7. Accessing from another PC

On any PC connected to the department intranet, open a browser and go to:

```
http://192.168.1.50:8080
```

(Replace `192.168.1.50` with your server's IP and `8080` with your port.)

### Default logins

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | `admin`  | `admin123` |
| User  | `user`   | `user123`  |

Change these passwords as soon as possible. See section 13 (updating).

---

## 8. Firewall configuration

Windows Firewall may block outside PCs from reaching the server. To allow
the application through **once**:

1. Open **Windows Defender Firewall → Advanced settings → Inbound Rules**.
2. Click **New Rule → Port**.
3. Select **TCP**, and enter the port the application uses (e.g. `8080`).
4. **Allow the connection** → tick all profiles → name it `SOR App` → **Finish**.

If the department uses any other firewall between PCs, ask the network
administrator to open the same TCP port.

> Test from another PC: if you can open the login page from another PC, the
> firewall is configured correctly.

---

## 9. Multiple users and shared data

- There is exactly **one database** — the file `database\sor.db` on the
  server.
- Every user (on any PC) reads and writes that same file.
- When an Admin adds, edits or deletes an entry, the change is saved
  immediately to the server database. Other users see it as soon as they
  search or refresh their page.
- Do **not** copy `database\sor.db` between PCs, and do not edit it by hand.

---

## 10. Keeping data safe

### Back up the database

The application already snapshots the database into `backup\` automatically
every time it starts (newest 14 kept — see section 14). For extra safety,
copy the `database` folder to another PC or a pen drive on a convenient
schedule:

1. Stop the application (section 12).
2. Copy the `database` folder (and optionally `config` and `logs`) to a safe
   place.
3. Restart the application.

To restore a backup, stop the application, copy the saved `database\sor.db`
back over the current one, and start the application again.

> Because the database uses SQLite's WAL mode, always stop the application
> before copying the database files.

### Update the application

1. Stop the application.
2. Back up the `database` folder (and `config`).
3. Replace `Application.exe` with the new one (from a fresh build).
4. Start `Application.exe`. Your data is untouched because it lives in the
   `database` folder, not inside the exe.

---

## 11. Starting the server automatically (optional)

To avoid starting the server by hand after a reboot:

1. Press **Win + R**, type `taskschd.msc`, press Enter.
2. Click **Create Task** (right side).
3. **General**: Name `SOR Server`, tick *Run whether user is logged on or
   not*.
4. **Triggers → New**: *At startup* → OK.
5. **Actions → New**: *Start a program* → Program: browse to
   `C:\SOR\Application\Application.exe` → OK.
6. **Settings**: tick *Restart if the task fails* (e.g. every 1 minute, 3
   times) → OK.

---

## 12. Stopping the server

- Click the server's console window and press **Ctrl + C** (or **X** to close
  the window), **or**
- Open Task Manager, find **Application.exe**, and choose *End task*.

Stopping the server is safe at any time — the database is transaction-safe
and will not be corrupted. Simply start `Application.exe` again to resume.

---

## 13. Changing the default admin password

Default passwords are risky on a real intranet. To change them:

1. Stop the application.
2. Delete the database file `database\sor.db` (only if you have no real data
   yet).
3. Edit `db.py`? — **no**: instead, after the first run you can simply log in
   and add/remove entries through the Manage screen. For login accounts,
   change `DEFAULT_ADMIN_PASSWORD` / `DEFAULT_USER_PASSWORD` in the source,
   rebuild with `python build.py`, then delete `database\sor.db` so the new
   defaults are seeded.

> If you already have real data and still need to change passwords, ask your
> IT support to edit the database or add a user-management screen. Contact
> the developer for a supported procedure.

---

## 14. Where things are

| Item                  | Location (next to Application.exe) |
|-----------------------|------------------------------------|
| Database              | `database\sor.db`                  |
| Settings              | `config\config.ini`                |
| Logs (rotating)       | `logs\app.log` (old: app.log.1, ...) |
| Uploads / Exports / Backups | `uploads\`, `exports\`, `backup\` (reserved) |

### Automatic backups

Every time the application starts, it copies the database into `backup\`
using SQLite's online backup (safe even while users are working). Files are
named `sor_YYYYMMDD_HHMMSS.db`; the newest 14 are kept, older ones are
deleted automatically.

To restore: stop the application, copy the wanted backup file over
`database\sor.db`, then start the application again.

---

## 15. Troubleshooting

| Problem | Likely cause and fix |
|---------|----------------------|
| Other PCs cannot open the page | Wrong IP, or firewall blocking the port. Re-check `ipconfig` (section 6) and the firewall rule (section 8). |
| "Could not start server ... address already in use" | Another program uses the port. Change the port (section 5) or stop that program. If a previous run was killed forcefully (e.g. ended from Task Manager), a leftover process may still hold the port — open Task Manager, end any **Application.exe** process, then start again. |
| Login page loads but search shows nothing | Server database is empty — on a fresh install first run should seed 2,154 entries. Check `logs\app.log`. |
| The app window closes immediately | A startup error occurred. Open a Command Prompt, run `Application.exe` there, and read the message. Check `logs\app.log`. |
| Data seems lost after restart | Make sure `Application.exe` is started from the same folder — data is stored next to the exe. Never run a second copy from another folder. If the database is missing or damaged, restore the newest file from `backup\`. |
| Page is slow | Increase `threads` in `config\config.ini` (e.g. 16) and restart. |
| Need more help | Ask your IT support to inspect `logs\app.log` and contact the application developer with that file. |

---

## 16. Production checklist

- [ ] Application folder copied to the server.
- [ ] Server started and login page loads on the server itself.
- [ ] Login page loads from another PC via `http://SERVER_IP:PORT`.
- [ ] Firewall rule added for the chosen TCP port.
- [ ] Default admin password changed (for real deployment).
- [ ] Database backup copied somewhere safe.
- [ ] (Optional) Scheduled task created for auto-start.
