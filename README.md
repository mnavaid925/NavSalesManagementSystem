# Salezy — Sales Management System

A multi-tenant **Sales Management System** built with **Django 5.1** (backend) and
**Tailwind CSS + HTMX** (frontend). Clean, fully responsive blue/white dashboard with a
full layout customizer (dark mode, RTL, sidebar variants, boxed/fluid, and more).

This repository currently ships the **foundation + Modules 0–10**:

- Multi-tenant core (isolated workspaces, tenant middleware, audit log)
- Authentication — login, self-service registration (tenant onboarding), forgot/reset password, invitation acceptance
- User management — users, invitations, roles, profile & password change
- The blue/white **dashboard** (KPIs, revenue chart, sales gauge, recent sales) wired to live tenant data
- **Module 0 — Tenant & Subscription Management** (5 sub-modules, full CRUD)
- **Modules 1–10** — Leads, Opportunities & Pipeline, Contacts & Accounts (CRM), Forecasting, Quotes &
  Proposals, Orders, Territories & Quotas, Sales Activities & Tasks, Sales Enablement, and Incentive
  Compensation — each 5 sub-modules, ~5 tenant-scoped models, full CRUD (list/search/filter/paginate +
  detail + create + edit + delete) and an idempotent seeder
- Migrations, idempotent seeders (fake data via Faker), and the `.env`-driven MySQL config

Modules 11–20 from [`SalesManagementSystem.md`](SalesManagementSystem.md) appear in the sidebar as
**roadmap placeholders** and are delivered one at a time.

---

## Tech stack

| Layer | Choice |
|-------|--------|
| Backend | Django 5.1 (function-based views) |
| Frontend | Tailwind CSS (Play CDN) + HTMX + Chart.js + Lucide icons |
| Database | MySQL / MariaDB (XAMPP) via **PyMySQL** |
| Auth | Custom `accounts.User` (email-or-username login) |
| Seeders | Faker |
| Tests | pytest + pytest-django (SQLite, isolated) |

> **MariaDB 10.4 note:** XAMPP ships MariaDB 10.4 but Django 5.1 expects ≥ 10.5.
> `config/__init__.py` applies a compatibility shim (lowers the version floor and disables
> `INSERT … RETURNING`). No action needed — it's automatic.

---

## Prerequisites

- **Python 3.11** (3.10–3.13 supported)
- **XAMPP** running **MySQL/MariaDB** on `127.0.0.1:3306` (default `root` / no password)

## Setup

```powershell
# 1. Virtual environment
py -3.11 -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Environment file
copy .env.example .env      # adjust DB credentials if your XAMPP differs

# 3. Create the database (utf8mb4)
& "C:\xampp\mysql\bin\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS nav_sms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. Migrate
venv\Scripts\python.exe manage.py migrate

# 5. Seed demo data (idempotent)
venv\Scripts\python.exe manage.py seed_demo       # tenants, roles, users, invites (run first)
venv\Scripts\python.exe manage.py seed_tenants    # Module 0: subscriptions, invoices, keys, branding, health
# Modules 1-10 (each idempotent; run after seed_demo):
venv\Scripts\python.exe manage.py seed_leads
venv\Scripts\python.exe manage.py seed_opportunities
venv\Scripts\python.exe manage.py seed_crm
venv\Scripts\python.exe manage.py seed_forecasting
venv\Scripts\python.exe manage.py seed_quotes
venv\Scripts\python.exe manage.py seed_orders
venv\Scripts\python.exe manage.py seed_territories
venv\Scripts\python.exe manage.py seed_activities
venv\Scripts\python.exe manage.py seed_enablement
venv\Scripts\python.exe manage.py seed_compensation

# 6. Run
venv\Scripts\python.exe manage.py runserver
```

Open <http://127.0.0.1:8000/> → you'll be redirected to the login page.

## Demo credentials

| Account | Username | Password | Notes |
|---------|----------|----------|-------|
| Tenant admin (Acme) | `admin_acme` | `password123` | Sees Acme's data |
| Tenant admin (Globex) | `admin_globex` | `password123` | Sees Globex's data |
| Platform superuser | `admin` | `admin123` | `/admin` only — **no tenant**, so module data is hidden by design |

> Data is **tenant-scoped**. The superuser has no tenant, so log in as a tenant admin to see the dashboard and Module 0 data.

---

## Dashboard & layout features

- **Theme:** clean blue & white, light **and** dark mode
- **Customizer** (gear icon, top-right) persists to `localStorage`:
  - Sidebar layout: vertical / horizontal / detached
  - Layout width: fluid / boxed · position: fixed / scrollable
  - Topbar: light / dark · Sidebar size: default / compact / small-icon / icon-hover · Sidebar color: light / colored
  - Direction: **LTR / RTL** · Preloader: on / off
- Fully responsive (desktop → mobile drawer), Chrome/Firefox/Safari/Edge compatible

---

## Module roadmap

| # | Module | Status |
|---|--------|--------|
| 0 | Tenant & Subscription Management | ✅ **Complete** |
| 1 | Lead Management | ✅ **Complete** |
| 2 | Opportunity & Pipeline Management | ✅ **Complete** |
| 3 | Contact & Account Management | ✅ **Complete** |
| 4 | Sales Forecasting | ✅ **Complete** |
| 5 | Quote & Proposal Management | ✅ **Complete** |
| 6 | Order Management | ✅ **Complete** |
| 7 | Territory & Quota Management | ✅ **Complete** |
| 8 | Sales Activity & Task Management | ✅ **Complete** |
| 9 | Sales Enablement | ✅ **Complete** |
| 10 | Incentive Compensation Management | ✅ **Complete** |
| 11 | Customer Success & Account Management | 🔜 Roadmap |
| 12 | Sales Analytics & Intelligence | 🔜 Roadmap |
| 13 | Marketing Alignment & Attribution | 🔜 Roadmap |
| 14 | Partner & Channel Management | 🔜 Roadmap |
| 15 | Contract & Subscription Management | 🔜 Roadmap |
| 16 | Mobile Sales | 🔜 Roadmap |
| 17 | Workflow & Process Automation | 🔜 Roadmap |
| 18 | Integration & API Hub | 🔜 Roadmap |
| 19 | Master Data & Configuration | 🔜 Roadmap |
| 20 | System Administration & Security | 🔜 Roadmap |

### Module 0 sub-modules (live)

| Sub-module | Where |
|------------|-------|
| Tenant Onboarding | `/tenant/onboarding/` |
| Subscription & Billing | `/tenant/subscriptions/`, `/tenant/invoices/` |
| Tenant Isolation & Security | `/tenant/security/keys/`, `/core/audit-log/` |
| Custom Branding | `/tenant/branding/` |
| Tenant Health Monitoring | `/tenant/health/` |

### Modules 1–10 (live)

Each module is a Django app under `apps/<slug>/` with ~5 tenant-scoped models, full CRUD, and an
idempotent `seed_<slug>` command. All 5 sub-modules of every module resolve as **Live** in the sidebar.

| # | Module | App / base URL |
|---|--------|----------------|
| 1 | Lead Management | `apps/leads` — `/leads/` |
| 2 | Opportunity & Pipeline Management | `apps/opportunities` — `/opportunities/` |
| 3 | Contact & Account Management | `apps/crm` — `/crm/` |
| 4 | Sales Forecasting | `apps/forecasting` — `/forecasting/` |
| 5 | Quote & Proposal Management | `apps/quotes` — `/quotes/` |
| 6 | Order Management | `apps/orders` — `/orders/` |
| 7 | Territory & Quota Management | `apps/territories` — `/territories/` |
| 8 | Sales Activity & Task Management | `apps/activities` — `/activities/` |
| 9 | Sales Enablement | `apps/enablement` — `/enablement/` |
| 10 | Incentive Compensation Management | `apps/compensation` — `/compensation/` |

---

## Project structure

```
config/        settings, URLs, PyMySQL + MariaDB shim
apps/core/     Tenant, AuditLog, tenant middleware, sidebar navigation catalog
apps/accounts/ custom User, Role, UserInvite + auth & user-management views
apps/dashboard/ the overview dashboard
apps/tenants/  Module 0 — Tenant & Subscription Management
apps/leads/ opportunities/ crm/ forecasting/ quotes/ orders/
apps/territories/ activities/ enablement/ compensation/   Modules 1-10
templates/     base + auth layouts, partials, per-module pages
static/        css/theme.css, js/layout.js
```

## Testing

```powershell
venv\Scripts\python.exe -m pytest        # uses config.settings_test (in-memory SQLite)
```

## Development notes

- Every tenant-scoped view filters `Model.objects.filter(tenant=request.tenant)`.
- New modules are scaffolded with the `/next-module` workflow, mirroring `apps/tenants`.
- Commits are one file per commit; pushes are manual.

## Security & production checklist

Built in: tenant isolation (cross-tenant access → 404), `@tenant_admin_required` on workspace writes, CSRF on all POST
forms, hashed passwords + `AUTH_PASSWORD_VALIDATORS`, encryption-key secrets stored as prefix+hash and revealed once,
hex-validated branding colours, open-redirect-safe `next`, fail-closed `SECRET_KEY`, and (when `DEBUG=False`) secure
cookies + SSL redirect + HSTS. Demo credentials only render when `DEBUG=True`.

Before deploying to production:
- Set a strong `SECRET_KEY` and `DEBUG=False` in the environment.
- Add **login rate-limiting / lockout** (e.g. `django-axes`) — intentionally not bundled in this foundation.
- Use a real MariaDB ≥ 10.5 / MySQL 8 so the `config/__init__.py` 10.4 compatibility shim is unnecessary.
- Serve over HTTPS and run `collectstatic`.
