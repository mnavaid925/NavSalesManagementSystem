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

## Phase E/F — Page templates (Workflow fan-out) — IN PROGRESS
- [ ] tenants subscription/invoice/encryptionkey/branding/health trios; accounts user/role/invite/profile; auth reset/invite — via `sms-templates-fanout`
- [x] Reference set hand-written: base, partials, dashboard, login, register, roadmap, audit_log, onboarding trio + overview

## Phase H — Verification + mandatory review sequence — TODO
- [ ] manage.py check 0 issues; temp/smoke.py (200/302, IDOR→404, no comment leaks, content assertions)
- [ ] Live browser verify (dashboard, auth, user mgmt, Module 0, dark/customizer/RTL) + screenshot
- [ ] code-reviewer → explorer → frontend-reviewer → performance-reviewer → qa-smoke-tester → security-reviewer → test-writer (commit after each)
- [ ] README updated (done); pytest green

## Review
_(to be completed after Phase H)_
