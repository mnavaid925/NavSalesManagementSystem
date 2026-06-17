---
name: next-module
description: Scaffold and build the NEXT NavPMS module end-to-end (Modules 1–20 from ProjectManagementSystem.md) — a Django app under apps/<slug> with tenant-scoped models, full CRUD views/forms/urls/admin, Tailwind+HTMX templates, an idempotent seeder, navigation wiring, and migrations — following the Module 0 (apps/tenants) reference patterns. Use when the user says "new", "next", "new module", "next module", "build the next module", "create the next module", "continue the modules", "scaffold the next module", or invokes /next-module. Optional argument: a specific module number 1–20 (e.g. "/next-module 3") or a module name; with no argument, auto-detect the lowest-numbered module not yet built.
---

# next-module — NavPMS module builder

When this skill is invoked, you build **one complete NavPMS module** end-to-end, matching the conventions
already established in the codebase. Module 0 (**Tenant & Subscription Management**, the `apps/tenants` app)
is the **canonical reference implementation** — read it whenever you are unsure how something should look.

## Triggers
- User says: **"new"**, **"next"**, "new module", "next module", "build/create the next module", "continue the modules", "scaffold module N".
- User invokes **`/next-module`** (optionally with a module number `1`–`20` or a module name).

## When NOT to use
- User wants tests for a module → `/manual-test` or `/sqa-review`.
- User wants a code dump → `/dump-module`.
- User wants to fix a specific bug → just fix it.
- User wants to change Module 0 / the dashboard / auth → edit those directly, this skill is for **new** modules 1–20.

---

## Project conventions (the real, as-built NavPMS — NOT the procurement sibling)

> ⚠️ The `dump-module` / `manual-test` skills in this repo were copied from a different (procurement)
> project and describe Bootstrap / class-based mixins / `Welcome@123`. **Ignore them for patterns.** The
> live app is the one below.

- **Stack:** Django 5.1, **function-based views** with `@login_required`, **Tailwind CSS (Play CDN) + HTMX +
  Chart.js + Lucide**, MySQL/MariaDB (XAMPP) via PyMySQL. DB is **`nav_pms`**. Run Python through the venv:
  `venv\Scripts\python.exe manage.py ...` (PowerShell) — Django is not on system Python.
- **App layout:** `apps/<slug>/`, AppConfig `name = 'apps.<slug>'`. Register in `config/settings.py`
  `INSTALLED_APPS` and add `path('<slug>/', include('apps.<slug>.urls'))` to `config/urls.py`.
- **Templates:** project-level `templates/<slug>/...`, **extend `templates/base.html`**, use the design-system
  classes from `static/css/theme.css`: `.page-header .page-title .breadcrumb .page-actions`, `.card .card-header
  .card-body`, `.btn .btn-primary .btn-outline .btn-danger .btn-icon`, `.badge .badge-success/.warning/.danger/
  .info/.muted` (+ color variants), `.table-wrap .table .table-actions`, `.form-group .form-label .form-input
  .form-select .form-textarea .form-error`, `.stat-card`, `.empty-state`, `.pagination`, `.avatar-initial`,
  `.progress .progress-bar`. Icons: `<i data-lucide="NAME"></i>`.
- **Multi-tenancy (mandatory):** every model has `tenant = models.ForeignKey('core.Tenant',
  on_delete=models.CASCADE, related_name='<unique>')`. Every view filters `Model.objects.filter(tenant=request.tenant)`
  — never `.all()`. `request.tenant` is set by `apps.core.middleware.TenantMiddleware`.
- **CRUD completeness (mandatory):** every model with a list page gets **list (search + filters + pagination),
  detail, create, edit, delete (POST-only + confirm + csrf)**. List templates have an Actions column
  (view/edit/delete). See CLAUDE.md "CRUD Completeness Rules" + "Filter Implementation Rules".
- **Filters:** parse `request.GET` and apply BEFORE pagination. Pass `status_choices` + any FK querysets the
  template's filter dropdowns need. pk filters compare with `|stringformat:"d"`.
- **Seeders:** idempotent (guard `if Model.objects.filter(tenant=tenant).exists()`), `get_or_create`,
  existence-check auto-numbers. Create both `management/__init__.py` and `management/commands/__init__.py`.
- **Auto-numbers:** human-readable per-tenant numbers like `RSK-00001`, `REQ-00001` where it fits.
- **Git:** at the end, output a **PowerShell-safe one-file-per-commit** snippet (`git add 'f'; git commit -m '...'`).
  Do NOT commit yourself — the user commits.
- **Security:** flag vulnerabilities with a `# WARNING:` comment + secure alternative.

Reference files to read before building: `apps/tenants/models.py`, `apps/tenants/views.py`, `apps/tenants/urls.py`,
`apps/tenants/forms.py`, `apps/core/navigation.py`, `templates/tenants/*.html`, `static/css/theme.css`,
`apps/core/management/commands/seed_demo.py`.

---

## Step 1 — Decide which module to build

1. **If the user passed an argument, resolve it to exactly one module** (the argument may be a number, a name,
   a keyword, or an app slug — all are accepted, case-insensitive, punctuation/`&`/`and` ignored):
   - **Number** — `1`–`20` (also `01`, `#3`, `module 5`) → that module.
   - **App slug** — a value from the table below (e.g. `risks`, `planning`, `finance`) → that module.
   - **Full or partial module name** — match against the `MODULE_CATALOG` names in `apps/core/navigation.py`
     (e.g. `Risk & Issue Management`, `risk issue`, `risk`, `scheduling`, `agile`, `time tracking`). Do a
     case-insensitive substring/keyword match on the module name **and** its app slug.
   - **Sub-module name** — if the text matches a sub-module (e.g. `Kanban`, `WBS`, `timesheets`), build that
     sub-module's parent module.
   - If the text matches **more than one** module (ambiguous) → ask the user to pick via `AskUserQuestion`
     (list the candidate modules). If it matches **none** → tell the user and show the module table.
   - If the resolved module's app already exists under `apps/`, say so and ask whether to extend it or pick another.

   Examples: `/next-module 5`, `/next-module risks`, `/next-module "Risk & Issue Management"`,
   `/next-module risk`, `"build the Agile module"`, `"create Resource Management"` all resolve to one module.

2. **If no argument**, **auto-detect the next module**: the lowest `N` in `1..20` whose app slug (table below)
   does NOT yet exist under `apps/`. (Module 0 = `apps/tenants` is already built, so the first run targets
   **Module 1**.) Confirm by checking the directory and by reading `apps/core/navigation.py` `LIVE_LINKS`.
3. State which module you're building and proceed (enter plan mode per CLAUDE.md, present the short model/page
   spec for the 5 sub-modules, then build — lean toward building, don't over-deliberate).

### Module → app-slug + suggested models (covering the 5 sub-modules each)

| # | Module name | app slug | Suggested tenant-scoped models (adapt as needed) |
|---|---|---|---|
| 1 | Project Initiation & Charter | `initiation` | ProjectRequest, BusinessCase, ProjectCharter, Stakeholder, KickoffChecklist |
| 2 | Project Planning & Scheduling | `planning` | WorkPackage(WBS), ScheduleTask, TaskDependency, Milestone, ScheduleBaseline |
| 3 | Resource Management | `resources` | Resource, Skill, Allocation, DemandForecast, TimeEntry |
| 4 | Cost & Budget Management | `budgeting` | Budget, ControlAccount, Expense, CostForecast, BudgetChange |
| 5 | Risk & Issue Management | `risks` | Risk, RiskAnalysis, RiskResponse, Issue, RiskReview |
| 6 | Quality Management | `quality` | QualityStandard, QualityAudit, Inspection, ImprovementAction, DeliverableSignoff |
| 7 | Scope & Requirements Management | `scope` | Requirement, RequirementTrace, ScopeStatement, ChangeRequest, ScopeVerification |
| 8 | Task & Work Management | `work` | WorkItem, PriorityScore, BoardColumn, BoardCard, WorkDependency |
| 9 | Collaboration & Communication | `collaboration` | Channel, Message, SharedDocument, Notification, ActivityEntry |
| 10 | Document & Knowledge Management | `documents` | Document, DocumentTemplate, DocumentVersion, KnowledgeArticle, RetentionPolicy |
| 11 | Time & Attendance Tracking | `timesheets` | Timesheet, TimesheetLine, TimesheetApproval, LeaveRecord, UtilizationSnapshot |
| 12 | Portfolio & Program Management | `portfolio` | Portfolio, Program, ProgramDependency, StrategicGoal, CapacityPlan |
| 13 | Agile & Scrum Management | `agile` | Sprint, BacklogItem, Release, Epic, Retrospective |
| 14 | Client & External Collaboration | `clients` | ClientAccess, ClientFeedback, SOWContract, ExternalVendor, ClientInvoice |
| 15 | Financial & Billing Management | `finance` | CostCenter, FinanceInvoice, Payment, BudgetActual, CurrencyRate |
| 16 | Reporting & Business Intelligence | `reporting` | ReportDefinition, ReportRun, DashboardWidget, ExecutivePack, DataExport |
| 17 | Workflow & Automation | `automation` | WorkflowDefinition, ApprovalRule, NotificationRule, RecurringRule, AutomationHook |
| 18 | Integration & API Hub | `integrations` | Connector, SyncJob, SyncLog, Webhook, ApiKey |
| 19 | Master Data & Configuration | `masterdata` | ProjectTemplate, CustomField, OrgUnit, Team, LocalizationSetting |
| 20 | System Administration & Security | `administration` | SecurityPolicy, ComplianceItem, BackupJob, SystemHealthMetric, AccessReview |

Aim for **3–6 models** per module so each of the 5 sub-modules maps to a real list page (or a logical page).
For Modules 19 & 20, some sub-modules already have live pages (`accounts:role_list`, `accounts:user_list`,
`core:audit_log`) — keep those mappings and only build the missing pieces.

---

## Step 2 — Build the module (prefer a parallel agent Workflow for speed)

The user prefers fanning work out across agents. For a single module a small **2–3 agent Workflow** works well:
keep **backend + migrations + seed** as one solo agent (single DB writer), then **templates** as 1–2 agents.
You may also build it inline if it's quick. Either way produce ALL of the following:

### 2a. Backend (`apps/<slug>/`)
- `apps.py` (`name='apps.<slug>'`, `verbose_name`), `__init__.py`.
- `models.py` — the 3–6 models above. Each: `tenant` FK, timestamps (mirror `apps/tenants` base or add
  `created_at/updated_at`), `STATUS_CHOICES` class attrs where relevant, `__str__`, `class Meta: ordering`.
  Reuse `apps.projects.models.Project` as an FK where a model belongs to a project (import lazily by string
  `'projects.Project'`). Auto-number in `save()` or the view with an existence guard.
- `forms.py` — ModelForms; **exclude** `tenant` and auto-`number` (set them in the view).
- `views.py` — function-based, `@login_required`, tenant-scoped, full CRUD + search + filters + pagination
  (copy the shape from `apps/tenants/views.py`). Write an `AuditLog` row on meaningful changes via the same
  helper the tenants app uses (`apps.core.utils` log helper).
- `urls.py` — `app_name='<slug>'`, names `<entity>_list/_detail/_create/_edit/_delete` per model.
- `admin.py` — register every model.
- `migrations/__init__.py` (+ generated `0001_initial.py`).
- `management/__init__.py`, `management/commands/__init__.py`, `management/commands/seed_<slug>.py`
  (idempotent Faker seeder for both demo tenants; mirror `seed_demo`'s per-tenant guard + summary print).

### 2b. Wire-up
- `config/settings.py`: add `'apps.<slug>'` to `INSTALLED_APPS`.
- `config/urls.py`: add `path('<slug>/', include('apps.<slug>.urls'))`.
- `apps/core/navigation.py`: add entries to `LIVE_LINKS` mapping each of the module's 5 sub-modules
  `(<module_number>, '<exact sub-module name from MODULE_CATALOG>')` → `'<slug>:<entity>_list'` (or the most
  relevant live page). After this, the sidebar shows that whole module as **Live** instead of placeholder.
  Do not change `MODULE_CATALOG` (the names/descriptions are already correct).

### 2c. Frontend (`templates/<slug>/`)
- For each model: `<entity>_list.html`, `<entity>_detail.html`, `<entity>_form.html` (shared create/edit).
- Extend `base.html`; use the design-system classes; list pages get a GET filter form (search `q` + status/FK
  selects reflecting `request.GET`), an Actions column (view/edit/delete POST+confirm+csrf), pagination, and an
  `.empty-state`. Badges use the model's exact choice values + `{{ obj.get_<field>_display }}` fallback. Add a
  module landing/overview page if helpful (stat cards summarizing the module).

### 2d. Migrate + seed + verify (venv python)
```
venv\Scripts\python.exe manage.py makemigrations <slug>
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py seed_<slug>
venv\Scripts\python.exe manage.py seed_<slug>   # 2nd run must be idempotent
venv\Scripts\python.exe manage.py check
```

---

## Step 3 — Verify (don't mark done until proven)

Render every new page as a tenant admin against seeded data and assert no errors / no leaks. Use a throwaway
script in `temp/` (gitignored) like the foundation smoke test:

- Log in via Django test client `force_login(User.objects.get(username='admin_acme'))` (set
  `settings.ALLOWED_HOSTS=['testserver',...]`), then GET every `<slug>:*` url (use `reverse`, sample a pk per
  model) and assert status in `(200, 302)`.
- Fetch one list page's HTML and assert **no** `'{#'` / `'{% comment'` leak markers (Django `{# #}` comments are
  single-line only — use `{% comment %}` for multi-line notes), and that the page title + a seeded record appear.
- Fix anything that isn't 200/302 (the usual culprit: a wrong reverse-accessor name or a context-variable
  mismatch — read the view to confirm the exact name).

Credentials: tenant admins `admin_acme` / `admin_globex`, password `password123`. The superuser `admin` has
`tenant=None` and sees no module data (by design).

---

## Step 4 — Document + commit snippet
1. Update `README.md` (mark the module complete in the roadmap; add `seed_<slug>` to the seeding section).
2. Update `.claude/tasks/todo.md` with a short review.
3. Output the **one-file-per-commit** PowerShell snippet for every created/changed file
   (`git add 'apps/<slug>/models.py'; git commit -m 'feat(<slug>): models (...)'` etc.), plus the edits to
   `config/settings.py`, `config/urls.py`, `apps/core/navigation.py`, `README.md`. One `git add` + one
   `git commit` per file — never bundle.

---

## Continue / repeat
If the user says "next" again after a module is done, repeat Step 1 (auto-detect now returns the next-lowest
unbuilt module) and build that one. Keep going module by module on request.

## Quality bar
A delivered module must: migrate cleanly to `nav_pms`; seed idempotently; pass `manage.py check`; have every
list page rendering 200 with working search/filters/pagination + Actions; appear as **Live** in the sidebar for
all 5 sub-modules; match the blue/white Tailwind design system; and isolate data per tenant. Would a staff
engineer approve it? If a piece feels hacky, redo it the elegant way before presenting.
