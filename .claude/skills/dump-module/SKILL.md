---
name: dump-module
description: Regenerate the consolidated <NN>_<slug>.txt code dump for one (or all) NavSalesManagementSystem modules into the temp/ folder. The .txt file contains every backend file from apps/<name>/ followed by every frontend template from templates/<name>/, with per-file separators. Use when the user says "dump module X", "regenerate the temp file for X", "extract code for module X", "give me a code dump of X", or invokes /dump-module. The user can pass a module number (0-20), an app folder name (tenants/accounts/core/dashboard plus the roadmap slugs like leads/opportunities/quotes), a friendly name (e.g. "subscription", "lead", "pipeline", "forecast"), or "all" to regenerate every module.
---

# dump-module — NavSalesManagementSystem module code-dump generator

This skill regenerates one (or all) of the consolidated `temp\<NN>_<slug>.txt` files that contain a single module's complete backend + frontend source code, for use in code review, hand-off, AI prompts, or archival.

NavSalesManagementSystem is a multi-tenant **Sales Management System** (Django 5.1 + Tailwind/HTMX/Chart.js/Lucide, MySQL/MariaDB via PyMySQL, DB `nav_sms`). Built today: **Module 0 = `apps/tenants`** (Tenant & Subscription Management — the flagship complete module) plus the foundation apps **`accounts` / `core` / `dashboard`**. Modules **1–20** from `SalesManagementSystem.md` are sidebar roadmap placeholders built on demand by the **`/next-module`** skill — until each is built, dumping it produces only a header and a "(no backend folder found ...)" note, which is expected.

## When to use

- User says: "dump module X", "regenerate temp file for X", "extract module X code", "give me the .txt for X", "refresh the tenants module dump", "dump the leads app", "rebuild all module dumps"
- User invokes `/dump-module` (with or without an argument)
- User explicitly references the `temp/` folder code dumps

## When NOT to use

- User wants documentation written for a module → use the README maintenance rule and edit `README.md`
- User wants automated tests / SQA review for a module → use `/sqa-review`
- User wants a manual click-through test → use `/manual-test`
- User wants to scaffold a brand-new module 1–20 → use `/next-module`
- User wants a code review → use `/review` or `/sqa-review`

## Inputs

The skill takes ONE positional argument — the module identifier. Accepted forms:

| Form                | Examples                                     |
|---------------------|----------------------------------------------|
| Module number       | `0`, `5`, `13`, `00`, `05`                   |
| App folder name     | `tenants`, `accounts`, `core`, `dashboard` (built); `leads`, `opportunities`, `crm`, `forecasting`, `quotes`, `orders`, `territories`, `activities`, `enablement`, `compensation`, `success`, `analytics`, `marketing`, `partners`, `contracts`, `mobile`, `automation`, `integrations`, `masterdata`, `administration` (roadmap) |
| Friendly keyword    | `subscription`, `users`, `lead`, `pipeline`, `deal`, `contact`, `forecast`, `quote`, `commission`, `renewal` |
| Bulk                | `all` (or `*`) — regenerates every registry entry |

If the user does NOT specify a module, ask them which one (single-select) before running the script — do not guess. Default to **tenants** (Module 0, the complete flagship) if they say "the module" with no name; **tenants** is also the richest CRUD surface (OnboardingStep/Subscription/Invoice/EncryptionKey/BrandingSetting/HealthMetric).

## How to run

The skill ships a single PowerShell script: `.claude\skills\dump-module\dump_module.ps1`. Invoke it via the **PowerShell** tool (the user is on Windows PowerShell 5.x):

```
& '.claude\skills\dump-module\dump_module.ps1' -Module <identifier>
```

Examples:

```
& '.claude\skills\dump-module\dump_module.ps1' -Module tenants
& '.claude\skills\dump-module\dump_module.ps1' -Module 0
& '.claude\skills\dump-module\dump_module.ps1' -Module leads
& '.claude\skills\dump-module\dump_module.ps1' -Module all
```

Notes:
- The script's `$RepoRoot` defaults to `C:\xampp\htdocs\NavSalesManagementSystem`.
- The script auto-creates `temp/` if missing.
- The script overwrites the matching `<NN>_<slug>.txt` file (idempotent — safe to re-run).
- `temp/` should be gitignored — no commit snippet needed for the generated `.txt`.
- The script prints one line per generated file: `OK  <slug>  <bytes>  ->  temp\<slug>.txt`.

## Output structure (per .txt file)

```
####################################################################################################
# MODULE <number>. <Title>
# Backend:  apps\<name>\
# Frontend: templates\<name>\
# Generated: <YYYY-MM-DD HH:MM:SS>
####################################################################################################

====================================================================================================
BACKEND  (apps\<name>\)
====================================================================================================

----------------------------------------------------------------------------------------------------
FILE: apps\<name>\admin.py
----------------------------------------------------------------------------------------------------
<file contents>

... (one block per .py / .json / .yml / .md / .ini file, sorted by full path, __pycache__ excluded)

====================================================================================================
FRONTEND  (templates\<name>\)
====================================================================================================

----------------------------------------------------------------------------------------------------
FILE: templates\<name>\subscriptions.html
----------------------------------------------------------------------------------------------------
<file contents>

... (one block per .html / .htm / .js / .css / .txt file, sorted by full path)
```

If a module's `apps\<name>\` or `templates\<name>\` folder does not exist yet (any unbuilt module 1–20), that section is replaced by `(no backend folder found at apps\<name>\)` / `(no frontend folder found at templates\<name>\)`.

## Module registry (kept in `dump_module.ps1`)

Module numbers follow `SalesManagementSystem.md` (Modules 0–20). **Module 0** (Tenant & Subscription Management → `apps/tenants`) is COMPLETE, alongside the foundation apps. **Modules 1–20** are forward-compatible registry rows that map to the `/next-module` roadmap app slugs; their folders are created only when `/next-module` builds them.

| # | Slug                | apps\            | templates\       | Status |
|---|---------------------|------------------|------------------|--------|
| 0 | `00_tenants`        | `tenants`        | `tenants`        | Built  |
| — | `accounts`          | `accounts`       | `accounts`       | Built (foundation: users/roles/auth) |
| — | `core`              | `core`           | `core`           | Built (foundation: tenant/audit/navigation) |
| — | `dashboard`         | `dashboard`      | `dashboard`      | Built (foundation: KPI aggregation) |
| 1 | `01_leads`          | `leads`          | `leads`          | Roadmap |
| 2 | `02_opportunities`  | `opportunities`  | `opportunities`  | Roadmap |
| 3 | `03_crm`            | `crm`            | `crm`            | Roadmap |
| 4 | `04_forecasting`    | `forecasting`    | `forecasting`    | Roadmap |
| 5 | `05_quotes`         | `quotes`         | `quotes`         | Roadmap |
| 6 | `06_orders`         | `orders`         | `orders`         | Roadmap |
| 7 | `07_territories`    | `territories`    | `territories`    | Roadmap |
| 8 | `08_activities`     | `activities`     | `activities`     | Roadmap |
| 9 | `09_enablement`     | `enablement`     | `enablement`     | Roadmap |
| 10 | `10_compensation`  | `compensation`   | `compensation`   | Roadmap |
| 11 | `11_success`       | `success`        | `success`        | Roadmap |
| 12 | `12_analytics`     | `analytics`      | `analytics`      | Roadmap |
| 13 | `13_marketing`     | `marketing`      | `marketing`      | Roadmap |
| 14 | `14_partners`      | `partners`       | `partners`       | Roadmap |
| 15 | `15_contracts`     | `contracts`      | `contracts`      | Roadmap |
| 16 | `16_mobile`        | `mobile`         | `mobile`         | Roadmap |
| 17 | `17_automation`    | `automation`     | `automation`     | Roadmap |
| 18 | `18_integrations`  | `integrations`   | `integrations`   | Roadmap |
| 19 | `19_masterdata`    | `masterdata`     | `masterdata`     | Roadmap |
| 20 | `20_administration`| `administration` | `administration` | Roadmap |

When `/next-module` builds one of the roadmap modules, the registry already covers it — no edit needed. If a NEW app/slug is added that is not in this table, append a row to the `$registry` and `$aliases` blocks in `dump_module.ps1`. The roadmap slugs above must stay in sync with the `Module → app-slug` table in `.claude/skills/next-module/SKILL.md`.

## After running

1. Show the user the printed `OK ... bytes` line(s).
2. Confirm the path: `temp\<slug>.txt`.
3. Do NOT propose a git commit for the .txt file — `temp/` is gitignored.
4. If the script reports "no backend folder found" or "no frontend folder found" for a module, surface that warning to the user. For a roadmap module (1–20) this simply means it hasn't been built yet — suggest `/next-module` to scaffold it. For a built module it would mean the folder name in the registry is stale.

## Workflow checklist

1. Resolve the module identifier from the user's request. If ambiguous, ask via `AskUserQuestion` (default to `tenants` if they said "the module" with no name).
2. Invoke the PowerShell script via the PowerShell tool with the resolved identifier.
3. Relay the script's `OK ... bytes` output to the user verbatim.
4. End the turn — no commits, no follow-up unless the user asks for more.
