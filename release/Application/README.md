# CHSS Schedule of Rates (SOR) — Search & Management

A simple, secure web application for searching and managing the CHSS Schedule
of Rates. Designed for hospital departments to use on their office network
(intranet) — **no internet required**.

---

## What Does This App Do?

- **Search** through thousands of SOR items by name or code, with instant
  results and category filtering.
- **Manage** SOR entries (add, edit, delete) if you are an admin.
- **Import** a new dataset from Excel and **export** the current data back to
  Excel.
- **Roll back** to a previous version if something goes wrong during import.
- Works entirely on your office network — nothing is sent to the internet.

---

## Quick Start (Deploy in 5 Minutes)

> **You only need one PC on your office network to act as the server.**
> Everyone else accesses it through their web browser — nothing is installed
> on their computers.

### What You Need

| Item | Details |
|------|---------|
| **Server PC** | Any Windows 10/11 PC (or Windows Server) with at least 512 MB RAM and 100 MB free disk space |
| **Client PCs** | Any PC on the same office network with Chrome, Edge, or Firefox |
| **Internet** | Not required after installation |

### Step-by-Step

1. **Copy the `Application` folder** to the server PC.
   For example, copy it to `C:\SOR\Application`.
   Make sure you copy the **entire folder**, not just the `.exe` file.

2. **Double-click `Application.exe`** on the server PC.
   A black window (console) will open — this is the server running.
   **Do not close this window.**

3. **Test it on the server itself.**
   Open any web browser on the server PC and go to:
   ```
   http://localhost:8080
   ```
   You should see a login page.

4. **Find the server's IP address.**
   On the server PC, open a Command Prompt and type:
   ```
   ipconfig
   ```
   Look for the **IPv4 Address** (something like `192.168.1.50`).

5. **Access from any other PC on the network.**
   On any other PC, open a browser and go to:
   ```
   http://192.168.1.50:8080
   ```
   (Replace `192.168.1.50` with your server's actual IP address.)

6. **Log in with the default credentials:**

   | Role | Username | Password |
   |------|----------|----------|
   | Admin | `admin` | `admin123` |
   | User | `user` | `user123` |

   **Change these passwords before real use!** See the Deployment Guide
   for instructions.

That's it — the app is running!

---

## How to Use the App

### Searching (All Users)

1. Log in with your username and password.
2. You'll see the **Search** page with a search bar at the top.
3. Type a service name or SOR code — results appear instantly as you type.
4. Use the **category filter** below the search bar to narrow results to a
   specific department (e.g. Cardiology, Radiology, etc.).
5. Results show the SOR code, service name, category, and rate (price).
6. Use the page numbers at the bottom to navigate through results.

### Managing SOR Items (Admin Only)

1. Log in as **admin**.
2. Click **Manage SOR** in the left sidebar.
3. From here you can:
   - **Add a new item** — click the green "+ Add SOR Item" button at the top.
   - **Edit an item** — click the "Edit" button next to any row.
   - **Delete an item** — click the red "Delete" button next to any row.

### Uploading a New Database from Excel (Admin Only)

If you receive an updated Excel file with new SOR rates:

1. Go to the **Manage SOR** page.
2. Scroll down to the **Database Tools** section.
3. Click **Choose File** and select your `.xlsx` or `.xls` file.
   The file must have columns: **sor number, title, category, price**.
4. Click **Upload & Replace Database**.
5. The app validates every row first. If anything is wrong (missing name,
   invalid code, etc.), it will show an error and **nothing will be changed**.
6. If everything is valid, the database is replaced. You can undo this with
   the **Rollback** button.

### Downloading the Database as Excel (Admin Only)

1. Go to the **Manage SOR** page.
2. Scroll down to **Database Tools**.
3. Click **Download Database as Excel**.
4. An `.xlsx` file will download with all current SOR data.

---

## Important Things to Know

### Your Data is Safe

- The app **automatically backs up** the database every time it starts.
  Backups are stored in the `backup` folder (up to 14 are kept).
- If you accidentally delete something, you can restore from a backup:
  1. Stop the app (close the console window or use Task Manager).
  2. Copy the desired backup file from `backup` over `database\sor.db`.
  3. Start the app again.

### Everything Stays in One Place

- All data lives in the `database` folder next to `Application.exe`.
- **Never** move the `.exe` file to a different folder without also moving
  the `database`, `config`, and `logs` folders.
- **Never** run two copies of the app from different folders at the same time.

### Updating the App

When a new version is available:

1. Stop the app on the server.
2. Back up the `database` folder (just copy it somewhere safe).
3. Replace `Application.exe` with the new version.
4. Start the app again. Your data is **not** affected.

---

## Folder Structure

After the first run, the `Application` folder will look like this:

```
Application/
├── Application.exe          ← the app (double-click to start)
├── database/
│   ├── sor.db               ← the main database (your data)
│   └── sor_rollback.db      ← backup for undo after Excel import
├── backup/                  ← automatic startup backups (up to 14)
├── config/
│   └── config.ini           ← settings (port, host, etc.)
├── logs/
│   └── app.log              ← error and activity log
├── uploads/                 ← temporary upload area
├── exports/                 ← temporary export area
├── README.md                ← this file
└── DEPLOY.md                ← detailed deployment guide
```

---

## Troubleshooting

| Problem | What to Do |
|---------|------------|
| **Other PCs can't open the page** | Check the server's IP address (`ipconfig`). Make sure the firewall allows connections on port 8080 (see DEPLOY.md section 8). |
| **"Port already in use" error** | Another app is using port 8080. Change the port in `config\config.ini` or stop the other app. |
| **App window closes immediately** | Open a Command Prompt, navigate to the Application folder, type `Application.exe`, and read the error message. Check `logs\app.log` for details. |
| **Search shows no results** | The database may be empty. Check `logs\app.log`. On a fresh install, 2,154 items should be loaded automatically. |
| **Data seems lost** | Make sure you're starting the app from the same folder every time. Check the `backup` folder for recent snapshots. |
| **Page loads slowly** | Increase the number of threads in `config\config.ini` (set `threads = 16` or higher) and restart the app. |
| **Need more help** | Ask IT support to check `logs\app.log` and contact the developer. |

---

## Default Login Credentials

| Role | Username | Password | What You Can Do |
|------|----------|----------|-----------------|
| Admin | `admin` | `admin123` | Search, add, edit, delete, import/export database |
| User | `user` | `user123` | Search only |

**Change these before deploying to real users.**

---

## For IT / Developers

See `DEPLOY.md` in this folder for:
- Firewall configuration
- Setting up automatic startup (Windows Task Scheduler)
- Changing passwords
- Configuration options (port, host, threads)
- Full troubleshooting guide

The source code is available at:
```
https://github.com/inayafir/SOR-deployment
```
