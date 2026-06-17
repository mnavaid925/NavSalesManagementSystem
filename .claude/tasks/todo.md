# Build Modules 16–20 (reporting, automation, integrations, masterdata, administration)

`/next-module 16-20` with parallel Workflows (user OK'd 99 agents; build used 30, review used 32).
Wiring + migrate + seed + verify done solo in the main thread (single DB writer).
Pattern reference: **apps/finance** (Module 15) — every file mirrors it exactly.

## Modules & models (5 each, tenant-scoped, full CRUD) — mirror apps/finance — DONE
- [x] **16 `reporting`** — ReportDefinition(RPT), ReportRun(RUN), DashboardWidget(WID), ExecutivePack(EP), DataExport(EXP)
- [x] **17 `automation`** — WorkflowDefinition(WF), ApprovalRule(APR), NotificationRule(NR), RecurringRule(RC), AutomationHook(HK)
- [x] **18 `integrations`** — Connector(CON), SyncJob(SJ), SyncLog(SL), Webhook(WH), ApiKey(AK)
- [x] **19 `masterdata`** — ProjectTemplate(PT), CustomField(CF), OrgUnit(OU, self-FK), Team(TM), LocalizationSetting(LOC)
- [x] **20 `administration`** — SecurityPolicy(SEC), ComplianceItem(CMP), BackupJob(BK), SystemHealthMetric(HM), AccessReview(AR)

## Build (Workflows) — DONE
- [x] Backend ×5 (one solo writer per app dir): 11 files each, 25 models, NO DB, NO shared files
- [x] Templates ×25 (per model): list + detail + form (75 templates). NOTE: 1st workflow was cut off mid-phase
      (automation 3/15, administration 14/15); a focused 6-agent follow-up workflow regenerated the missing trios.

## Wire-up (solo) — DONE
- [x] settings.py INSTALLED_APPS += apps.reporting/automation/integrations/masterdata/administration
- [x] config/urls.py += 5 include() lines
- [x] navigation.py LIVE_LINKS += 22 entries (role_list/user_list/audit_log already live for 19/20)

## Migrate + seed + verify (solo) — DONE
- [x] makemigrations ×5 + migrate (5 × 0001_initial, clean — no related_name clashes)
- [x] seed_* ×2 each → idempotent (2nd run skips both tenants)
- [x] manage.py check → 0 issues
- [x] Smoke test (temp/smoke_16_20.py): 185 checks, 0 failures — list/create/detail/edit 200, delete GET 302,
      cross-tenant IDOR → 404, filter params 200, no template-comment leaks

## Security (mandatory) — DONE
- [x] ApiKey — store only key_prefix + hashed_key; form excludes hashed_key (# WARNING); templates mask
- [x] Webhook.secret / AutomationHook.secret — # WARNING comments; masked in detail; EXCLUDED from forms (see review)

## Adversarial review (Workflow — 32 agents: 4 reviewers → per-finding verifiers) — DONE
- [x] 28 findings → 10 confirmed real (18 dismissed: finance-pattern / Django misreads / nitpicks)
- [x] Fixed: WebhookForm exposed plaintext `secret` → excluded (3 reviewers caught it) [[L20]]
- [x] Fixed: system `*_at` DateTimeFields on edit forms (DateInput truncates time) → removed from 8 forms [[L22]]
- [x] Fixed: Team / ComplianceItem / AccessReview unreachable from sidebar → cross-links on orgunit_list + securitypolicy_list
- [x] Fixed: dead `Project` import in automation/views.py
- [x] Re-verified: check 0 issues; smoke 185/0; targeted check confirms no `secret`/timestamp inputs + cross-links render

## Docs — DONE
- [x] README: roadmap table (16–20 ✅ Complete; "all 21 modules built"), 5 seed commands, 5 route rows
- [x] lessons.md: L20 (mask≠exclude for secrets), L21 (verify file counts after a cut-off workflow), L22 (system timestamps off forms)

## Review
Modules 16–20 delivered end-to-end via a 30-agent build workflow + a 6-agent gap-fill + a 32-agent adversarial
review, with solo single-writer DB/wire/verify in between.
- 25 models, 55 backend files, 75 templates; 5 clean 0001_initial migrations; `check` 0 issues; seeders idempotent.
- All 5 sub-modules per module are **Live** in the sidebar (19/20 reuse the pre-existing role/user/audit pages).
- Adversarial review found 2 genuine defect classes (Webhook secret exposure; date-widget-on-DateTimeField) plus a
  nav-reachability gap and a dead import — all fixed and re-verified. The 18 dismissed findings were correctly
  rejected (they matched the finance reference or misread Django widget/field behavior).
- Smoke (temp/smoke_16_20.py): 185 URLs/assertions — CRUD 200/302, cross-tenant IDOR→404, filters 200, no leaks.
- Security: secrets never round-tripped through a form; ApiKey stores only prefix+hash; all flagged with # WARNING.
