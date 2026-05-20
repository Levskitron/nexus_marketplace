# Nexus Marketplace — Installation Guide

This document lists everything you need to install and configure to run **Nexus Marketplace** locally (and optional production-style runs). For what the app does, see [README.md](README.md) and [userguide.md](userguide.md).

---

## 1. What you are installing

| Component | Purpose |
|-----------|---------|
| **Python 3.10+** | Runtime (the codebase uses modern type syntax; use **3.10**, **3.11**, or **3.12**). |
| **pip** | Installs Python dependencies from `requirements.txt`. |
| **Git** (optional) | Clone and update the repository. |
| **Virtual environment** (`venv`) | Isolates project packages from your system Python. **Strongly recommended.** |

The app uses **SQLite** (`nexus.db` in the project root). No separate database server install is required.

---

## 2. Install system prerequisites

### 2.1 Python

1. Install Python from [python.org](https://www.python.org/downloads/) (Windows/macOS) or your OS package manager (Linux).
2. Confirm version (should be **3.10 or newer**):

   ```bash
   python --version
   ```

   On some systems the command is `python3`:

   ```bash
   python3 --version
   ```

3. Confirm **pip** is available:

   ```bash
   python -m pip --version
   ```

### 2.2 Git (optional)

Install [Git](https://git-scm.com/downloads) if you want to clone the repo instead of using a ZIP download.

---

## 3. Get the source code

**With Git:**

```bash
git clone <repository-url>
cd nexus_marketplace
```

**Without Git:** download the project archive, extract it, and open a terminal in the extracted `nexus_marketplace` folder (the directory that contains `app.py` and `requirements.txt`).

---

## 4. Create and activate a virtual environment

Always run the following from the **project root** (same folder as `app.py`).

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If script execution is disabled, you may need (once, as Administrator) to allow the current user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Alternatively use **Command Prompt**:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### macOS / Linux (bash or zsh)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation, your prompt usually shows `(.venv)`. **Leave the venv activated** for all `pip` and `python` commands below.

---

## 5. Install Python dependencies

From the project root, with the virtual environment activated:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### What `requirements.txt` pulls in (summary)

- **Flask** — web framework  
- **Flask-SQLAlchemy**, **SQLAlchemy** — ORM / database  
- **Flask-WTF**, **WTForms**, **email-validator** — forms and email field validation  
- **Werkzeug** — passwords, uploads, utilities  
- **python-dotenv** — load `.env` into environment variables  
- **stripe** — Stripe Checkout and webhooks (optional for local browsing; required for real payments)  
- **gunicorn** — production WSGI server (Unix-like systems; optional for local dev)

If `pip install` fails, read the error: missing **Microsoft C++ Build Tools** is rare for this stack; usually failures are due to wrong Python version or network/proxy issues.

---

## 6. Environment variables (`.env`)

The app reads optional configuration from a **`.env`** file in the project root (via `python-dotenv` in `app.py`).

1. Copy the example file:

   ```bash
   copy .env.example .env
   ```

   On macOS/Linux:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set values as needed (see [`.env.example`](.env.example)):

   | Variable | Required for | Notes |
   |----------|----------------|-------|
   | `FLASK_SECRET_KEY` | Production / shared servers | Use a long random string. For quick local-only demos the app falls back to a dev default if unset. |
   | `STRIPE_SECRET_KEY` | Checkout / payments | From [Stripe Dashboard](https://dashboard.stripe.com/) (test keys start with `sk_test_`). If unset, checkout shows that Stripe is not configured. |
   | `STRIPE_WEBHOOK_SECRET` | Reliable order fulfillment via webhook | Signing secret for `checkout.session.completed` (starts with `whsec_`). Needed when Stripe calls your `/account/stripe/webhook` endpoint (e.g. deployed or tunneled local). |
   | `MAIL_USERNAME`, `MAIL_PASSWORD` | Sending mail from **Support** (SMTP) | Gmail example: use an [App Password](https://support.google.com/accounts/answer/185833) if 2FA is on. |
   | `SUPPORT_EMAIL` | Support form “to” address | Optional override; the app has a code default if unset. |

**Security:** Never commit `.env` or real API keys. The repo should keep only `.env.example` as a template.

---

## 7. Database and seed data

On first run, the application:

1. Creates SQLite tables (`nexus.db` in the project root).  
2. Ensures **shop categories** exist (same logic as `seed_categories.py`).

You do **not** need to run `seed_categories.py` for a normal first start unless you are scripting maintenance; `app.py` already calls `ensure_categories()` after `db.create_all()`.

To reset the database: stop the app, delete `nexus.db`, start the app again (you will lose all data).

If you pull changes that alter table definitions (for example removed columns) and see database errors, treat that the same way: delete `nexus.db` and restart, or apply your own SQL migration so the file matches the models.

---

## 8. Admin accounts (optional)

To create or reset built-in **admin** and **superadmin** users (password documented in the script):

```bash
python create_admin_users.py
```

Read the script output for the default password, then **change it** after first login if this is anything other than a throwaway local demo.

Admin UI is under the URL prefix **`/admin`**.

---

## 9. Run the development server

From the project root, with venv activated and dependencies installed:

```bash
python app.py
```

Open a browser at:

**http://127.0.0.1:5000/**

The app runs with Flask’s built-in server and `debug=True` when started this way (suitable for development only).

---

## 10. File uploads and static assets

- Product images are stored under **`static/images/products/`** (configured as `UPLOAD_FOLDER` in `app.py`).  
- Ensure that folder exists and is writable (it is usually present in the repo; if not, create it).

---

## 11. Optional: Stripe webhooks on your machine

Checkout redirects work with only `STRIPE_SECRET_KEY`. **Webhooks** let Stripe notify your app at `/account/stripe/webhook` when payment completes (important for production and for testing fulfillment without relying only on the success redirect).

Typical approach:

1. Install [Stripe CLI](https://stripe.com/docs/stripe-cli).  
2. Log in and forward events to your local app, for example:

   ```bash
   stripe listen --forward-to localhost:5000/account/stripe/webhook
   ```

3. Put the CLI-printed **webhook signing secret** into `.env` as `STRIPE_WEBHOOK_SECRET`.

---

## 12. Optional: production-style run with Gunicorn (Linux / macOS)

**Gunicorn** is included in `requirements.txt`. Example (replace `app:app` if your entrypoint differs — here the Flask instance is `app` in `app.py`):

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Set all production environment variables (especially `FLASK_SECRET_KEY`, Stripe keys, and mail) on the host or process manager. **Do not** rely on Flask’s debug server in production.

On **Windows**, Gunicorn is not supported; use **Waitress** or deploy on Linux/WSL if you need a non-debug server locally.

---

## 13. Editor / IDE (optional)

The team uses **Visual Studio Code**. Useful extensions:

- Python (Microsoft)  
- Pylance (optional, for typing and IntelliSense)

This is optional; any editor works.

---

## 14. Quick checklist

- [ ] Python **3.10+** installed  
- [ ] Repository in a local folder  
- [ ] `python -m venv .venv` and venv **activated**  
- [ ] `python -m pip install -r requirements.txt` completed  
- [ ] `.env` created from `.env.example` (at least for Stripe/email if you need those features)  
- [ ] `python app.py` → open **http://127.0.0.1:5000/**  
- [ ] (Optional) `python create_admin_users.py` for `/admin` access  

---

## 15. Troubleshooting

| Symptom | Things to check |
|---------|-------------------|
| `python` not found | Use `py` launcher on Windows, or `python3` on macOS/Linux. |
| Wrong Python version | Upgrade to 3.10+; recreate `.venv` after upgrading. |
| `ModuleNotFoundError` | Activate `.venv`, then reinstall: `python -m pip install -r requirements.txt`. |
| Port 5000 in use | Stop the other process or temporarily change the port in `app.py` (`app.run(debug=True, port=5001)`). |
| Stripe / checkout errors | `STRIPE_SECRET_KEY` in `.env`; use test keys for development. |
| Permission errors writing `nexus.db` | Run from a folder where your user can create files; avoid read-only copies. |

If something still fails, capture the **full terminal error** and the output of `python --version` and `python -m pip list`.
