# Build Modules 11–20 (Customer Success → System Administration)

Approach: parallel agent **Workflow** (≤35 agents) building each module from the
`apps/compensation` (Module 10) reference. Single-writer migrate/seed/verify done inline.

## Modules
- [ ] 11 `success` — Customer Success & Account Management (HealthScore, Renewal[REN-], OnboardingPlan, Advocacy, QBR)
- [ ] 12 `analytics` — Sales Analytics & Intelligence (WinLossAnalysis, SalesVelocity, ConversionFunnel, RepScorecard, Benchmark)
- [ ] 13 `marketing` — Marketing Alignment & Attribution (CampaignInfluence, MQLHandoff[MQL-], CampaignPerformance, ContentEngagement, MarketingEvent[EVT-])
- [ ] 14 `partners` — Partner & Channel Management (Partner, DealRegistration[DR-], PartnerCollateral, PartnerPerformance, ChannelConflict[CC-])
- [ ] 15 `contracts` — Contract & Subscription Management (Contract[CTR-], ContractClause, RenewalSchedule, UsageRecord, ContractObligation)
- [ ] 16 `mobile` — Mobile Sales (MobileDevice, FieldVisit[FV-], MobileQuote[MQ-], CallActivity, MobileAlert)
- [ ] 17 `automation` — Workflow & Process Automation (ProcessFlow, AssignmentRule, ApprovalWorkflow, AlertRule, EnrichmentRule)
- [ ] 18 `integrations` — Integration & API Hub (Connector, SyncJob[SYNC-], SyncLog, Webhook, ApiKey)
- [ ] 19 `masterdata` — Master Data & Configuration (ProductCatalog, CustomField, MethodologyConfig, PriceBook, LocalizationSetting)
- [ ] 20 `administration` — System Administration & Security (SecurityPolicy, DataPrivacyRule, ComplianceItem, BackupJob[BKP-], SystemHealthMetric)

## Phases
- [ ] Phase 1 — Build workflow: 10 agents, one per module, write `apps/<slug>/*` + `templates/<slug>/*` only (NO shared edits, NO migrations).
- [ ] Phase 2 — File-count check (L21): assert 15 templates + backend files per module before wiring.
- [ ] Phase 3 — Wire-up inline (L12/L24, after files exist): settings INSTALLED_APPS, config/urls includes, navigation LIVE_LINKS (47 new keys).
- [ ] Phase 4 — makemigrations + migrate + seed ×10 + 2nd seed (idempotency) + manage.py check. Fix errors inline.
- [ ] Phase 5 — Inline smoke test: all new urls 200/302 as admin_acme, content + comment-leak assertions, cross-tenant IDOR 404.
- [ ] Phase 6 — Specialist review workflow (security/perf/code/frontend per L18); apply critical fixes.
- [ ] Phase 7 — README roadmap update + per-file PowerShell commit snippet.

## Baked-in lessons
L7 pin every context var · L9 pagination partial · L10 guard FK display · L11 `.isdigit()` before int FK filter ·
L12/L24 wire-up after files exist · L20 EXCLUDE secret/key from ModelForm (Webhook.secret, ApiKey.key) ·
L21 verify file counts post-workflow · L22 no editable DateTimeField on forms (system `*_at` off form; DateInput only for user DateField) ·
Decimal: no computed Decimal @property arithmetic — store computed values as fields.

## Review (outcome)

**Status: Modules 11–20 built, wired, migrated, seeded, verified, reviewed & fixed. ✅**

- Build workflow: 10 agents, all returned 15 templates + 11 backend files. Disk check confirmed (L21).
- Wire-up (single writer, after files existed — L12/L24): settings (10 apps), urls (10 includes), navigation (47 LIVE_LINKS). `manage.py check` clean.
- Migrations: 10× `0001_initial` generated + applied to `nav_sms`. Seeders run twice → idempotent (no dup rows).
- Smoke test (`temp/smoke_11_20.py`): 50 models × list/create/detail/edit/delete = 250 GETs → **0 status failures, 0 comment leaks, 0 IDOR leaks**; detail pages contain record identifier (L8); sidebar 5/5 live for all 10 modules; auto-numbers + secret masking (off-form, L20) verified.
- Adversarial review workflow (10 reviewers + verifiers): 1 confirmed module-specific defect →
  - `automation` `EnrichmentRuleForm`: removed run-history counters `records_processed`, `success_rate` (system-set).
  - Cross-module sweep (L28) found the parallel defect missed by the per-module reviewer: `integrations` `SyncJobForm` `records_synced` → removed.
  - App-wide patterns (badge-color reuse; editable `roi`/`net_amount`/`commission_amount`) correctly NOT fixed per-module (faithful clones of the compensation reference — L18).
- Post-fix: `manage.py check` clean, smoke re-run ALL PASS, full `pytest` suite green.
- README updated (0–20 complete, seeding commands, live tables, structure).

### Per-module mandatory sequence (CLAUDE.md steps 2–8)

**Module 11 `success` — COMPLETE ✅** (run one agent at a time, commits between):
- code-reviewer: no module-specific changes (findings were faithful-clone app-wide patterns — L18).
- explorer: wiring complete (INSTALLED_APPS, urls, 5 LIVE_LINKS, namespace, seeder); only gap was missing tests (step 8).
- frontend-reviewer: no changes (one flagged `<th>` misalignment was a false positive — already correct; aria-label gap is clone-wide).
- performance-reviewer: **1 fix applied** — added `adv_tenant_acct_idx (tenant, account_name)` to `Advocacy` (only model whose default-ordering column lacked a composite index) + migration `0002`.
- qa-smoke-tester: 94 checks / ~70 requests, 0 failures — 200/302, no comment leaks, IDOR 404, delete POST-only, REN- numbering OK.
- security-reviewer: 0 Critical/High; all 3 Medium/Low findings are faithful-clone patterns (delete-on-GET no-op, Renewal.save() — note the suggested save() "fix" was a regression that releases the lock before INSERT; not applied).
- test-writer: **`apps/success/tests/` created** (conftest + models/forms/views/security) — **257 passed**. Full project suite: 2827 collected, all green; `manage.py check` clean.

### Outstanding
- **test-writer step for Modules 12–20** still pending — write `apps/<slug>/tests/` for the remaining 9 modules
  mirroring `apps/compensation/tests/` (models/forms/views/security + multi-tenant IDOR), one module at a time.
- Commit: user commits manually (one file per commit) — Module 11's commits are already made locally; user pushes.
