# Build: Foundation + Module 0 (Sales Management System)

Greenfield Django 5.1 + Tailwind/HTMX multi-tenant app. Backend built solo (single DB writer);
page templates fanned out via Workflow; closing review via the mandatory agent sequence.
Plan: `C:\Users\user\.claude\plans\valiant-yawning-map.md`.

## Phase A — Bootstrap — DONE
- [x] venv (py 3.11), pip install (Django 5.1, PyMySQL, Faker, python-dotenv, pytest, pytest-django) → requirements.txt
- [x] Create `nav_sms` DB (utf8mb4), `.env` + `.env.example`, pytest.ini, manage.py
- [x] config/: `__init__.py` (PyMySQL + MariaDB 10.4 shim), settings.py, settings_test.py, urls.py, wsgi/asgi

## Phase B — Core — DONE
- [x] Tenant, AuditLog models; TenantMiddleware; navigation.py (21 modules catalog + LIVE_LINKS)
- [x] context_processors (nav/tenant/layout), utils.log_action, roadmap + audit_log views, admin

## Phase C — Accounts (auth + users) — DONE
- [x] Custom User + Role + UserInvite; email-or-username backend
- [x] login / register (tenant onboarding) / forgot+reset / invite-accept
- [x] user + role + invite CRUD, profile, change password (all tenant-scoped, tenant-admin gated)

## Phase D — Dashboard — DONE
- [x] KPI cards + revenue chart + sales gauge + recent invoices, wired to live tenant data; empty-state for no-tenant

## Phase E — Layout & customizer — DONE
- [x] theme.css (blue/white + dark + RTL + all layout variants), layout.js (customizer + localStorage), base.html, base_auth.html, partials

## Phase F — Module 0 (tenants) — DONE
- [x] 6 models (OnboardingStep, Subscription, Invoice, EncryptionKey, BrandingSetting, HealthMetric) → 5 sub-module pages, full CRUD
- [x] EncryptionKey stores prefix+hash only, secret excluded from form, masked in templates (L20); system `*_at` off forms (L22)

## Phase G — Migrate + seed — DONE
- [x] makemigrations (Django auto-split accounts 0001/0002 to break the core↔accounts FK cycle); migrate clean to nav_sms
- [x] seed_demo (2 tenants, roles, admins, team, invites) + seed_tenants (Module 0 data); idempotent on 2nd run (counts stable)

## Phase E/F — Page templates (Workflow fan-out) — DONE
- [x] 9-agent Workflow `sms-templates-fanout` wrote tenants/accounts/auth page templates (mirroring the reference trio)
- [x] Reference set hand-written: base, partials, dashboard, login, register, roadmap, audit_log, onboarding trio + overview
- [x] 50 templates total; all compile; 0 comment leaks

## Phase H — Verification + mandatory review sequence — DONE
- [x] manage.py check 0 issues; temp/smoke.py 54 checks / 0 failures (200/302, IDOR→404, no comment leaks, content + secret-leak assertions)
- [x] Live browser verify: dashboard (live KPIs + Chart.js), dark mode, Module 0 CRUD, customizer; mobile grid collapse confirmed via computed styles
- [x] code-reviewer → explorer → frontend-reviewer → performance-reviewer → qa-smoke-tester → security-reviewer → test-writer (one at a time, committed after each)
- [x] pytest 342 passed; README updated

## Review
Foundation + Module 0 delivered end-to-end: multi-tenant Django 5.1 + Tailwind/HTMX, blue/white dashboard, full
layout customizer, auth (login/register/forgot/reset/invite), user/role/invite/profile management, and Module 0
(Tenant & Subscription Management — 6 models / 5 sub-modules, full CRUD). MariaDB 10.4 shim (L4/L23) lets Django 5.1
run on XAMPP. Sidebar lists all 21 modules (1–20 as roadmap placeholders).

**Mandatory review sequence outcomes (applied + committed per file):**
- code-reviewer: fixed a runtime blocker (`timezone.timedelta` → `datetime.timedelta` in invite_resend), atomic
  registration, seed skip bug, sidebar-cache DEBUG bypass.
- explorer: 0 contract mismatches (URLs/context/LIVE_LINKS/fields all consistent).
- frontend-reviewer: responsive grid classes (mobile collapse), removed a dead search box, htmx icon re-init, asset version bump.
- performance-reviewer: killed role_list N+1 (annotate), collapsed dashboard counts into 2 aggregates, added composite indexes.
- qa-smoke-tester: 87/87 green; added explicit ordering on annotated role_list.
- security-reviewer: one-time key reveal via session (not flash msg) [L25], hex-color validation [L26], tenant-admin
  gating on Module-0 writes [L27], fail-closed SECRET_KEY + HSTS, demo creds gated on DEBUG. Deferred login rate-limiting
  (django-axes) to production (documented in README).
- test-writer: 342 pytest tests (models, forms, views/CRUD, multi-tenant IDOR→404, authz, one-time reveal) — all pass.

**Verification:** `manage.py check` 0 issues · migrations clean · seeders idempotent · pytest 342/0 · smoke 54/0 · live browser confirmed.
Commits: one file per commit, never pushed (user pushes manually).
