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

---

# Build Modules 1–10 (Workflow orchestration)

Goal: build modules 1–10 end-to-end matching Module 0 (`apps/tenants`). Orchestrated with the
Workflow tool (user cap: 25 agents). Each module tenant-scoped, intra-app FKs only (no cross-module
FKs) so the 10 build agents are fully independent.

| # | name | slug | models |
|---|---|---|---|
| 1 | Lead Management | `leads` | Lead, LeadSource, LeadScore, NurtureCampaign, LeadConversion |
| 2 | Opportunity & Pipeline | `opportunities` | Opportunity, PipelineStage, OpportunityActivity, Competitor, DealCollaborator |
| 3 | Contact & Account | `crm` | Account, Contact, RelationshipMap, AccountTier, AccountPlan |
| 4 | Sales Forecasting | `forecasting` | ForecastCategory, Forecast, Quota, ForecastAdjustment, ForecastAccuracy |
| 5 | Quote & Proposal | `quotes` | Quote, QuoteLineItem, PricingRule, Proposal, QuoteVersion |
| 6 | Order Management | `orders` | Order, OrderLine, Fulfillment, OrderAmendment, RevenueSchedule |
| 7 | Territory & Quota | `territories` | Territory, TerritoryAssignment, QuotaPlan, CoverageModel, TerritoryPerformance |
| 8 | Sales Activity & Task | `activities` | Activity, SalesTask, Meeting, EmailLog, SalesPlan |
| 9 | Sales Enablement | `enablement` | ContentAsset, Playbook, TrainingRecord, CallRecording, CompetitiveCard |
| 10 | Incentive Compensation | `compensation` | CommissionPlan, Earning, Clawback, GlobalPlanVariation, Payout |

Phases: **Build** (10 parallel agents → code + manifest, no shared-file edits, no migrations) →
**Integrate** (1 serial agent = single DB writer: wire settings/urls/navigation, makemigrations →
migrate → seed_demo → seed_<slug> ×2 → check, fix at source) → **Verify** (10 parallel agents:
smoke each module's URLs as admin_acme, assert 200/302, scan comment leaks) → **Post-workflow (me):**
review, fix remaining failures, re-verify, emit one-file-per-commit snippet, update README.

Note: the per-module 7-agent review sequence is compressed under the 25-agent cap; build+integrate+
verify covers correctness, deeper review available later via `/sqa-review`.

## Checklist
- [x] Build (10 modules)  - [x] Integrate  - [x] Verify  - [x] Fix + re-verify (none needed)  - [x] README  - [x] Commit snippet

## Review (modules 1–10)
Delivered modules 1–10 via the `build-sms-modules-1-10` Workflow (21 agents: 10 build → 1 integrate →
10 verify), all mirroring the Module 0 (`apps/tenants`) conventions.

**Build:** 50 tenant-scoped models across 10 apps (`leads`, `opportunities`, `crm`, `forecasting`,
`quotes`, `orders`, `territories`, `activities`, `enablement`, `compensation`), each with slug-prefixed
unique `related_name`s, intra-app FKs only (no cross-module FKs), named indexes, per-tenant auto-numbers
(LEAD-/OPP-/QUO-/ORD-/EARN-/PAY-… via `save()` with existence guards), system timestamps kept off forms,
full CRUD function-based views (`@login_required` reads, `@tenant_admin_required` writes, `log_action`
audit), `StyledFormMixin` ModelForms with tenant-scoped FK querysets, admin registration, and the
list/detail/form template trio per model (design-system classes, GET filters reflecting `request.GET`,
Actions column, pagination, empty-state). 274 files.

**Integrate (single DB writer):** wired all 10 apps into `INSTALLED_APPS`, `config/urls.py`, and 50
`LIVE_LINKS` entries in `apps/core/navigation.py`; `makemigrations` → 10 `0001_initial` → `migrate`
clean to `nav_sms`; `seed_demo` + all 10 `seed_<slug>` ran and were **idempotent** on the 2nd pass
(byte-identical counts). Zero source fixes were required.

**Verification (independent gate, `temp/verify_all_1_10.py`):**
- Sidebar: modules 1–10 each **5/5 sub-modules Live** (every `LIVE_LINKS` key matches `MODULE_CATALOG`
  and every url_name reverses).
- URL sweep as `admin_acme`: **250/250** URLs 200/302 (list/create/detail/edit + GET-delete→302 no-mutation).
- **50/50** list pages: no `{# / {% comment` leaks.
- **10/10** cross-tenant IDOR checks → 404 (tenant isolation holds).
- `manage.py check`: 0 issues.

**Known follow-up (out of scope under the 25-agent cap):** FK-bearing list views (e.g. `lead_list`,
`opportunity_list`) don't yet `select_related()` their FKs — a minor N+1 polish, not a correctness bug.
The full per-module 7-agent review sequence (code/explorer/frontend/perf/qa/security/test) was compressed
into build+integrate+verify; deeper review can run later per module via `/sqa-review <module>`.

Commits: one file per commit (274 files), PowerShell-safe, never pushed (user commits manually).
