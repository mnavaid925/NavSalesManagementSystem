# Lessons

## L1 — Verify a database is actually ours (and empty) before migrating
`CREATE DATABASE IF NOT EXISTS x` is a **silent no-op** when `x` already exists. On this XAMPP instance,
`navpms` was already owned by a different Nav app (~170 procurement tables, live data). **Rule:** before
pointing `.env` at a DB and running migrate, check `SELECT COUNT(*) FROM information_schema.tables WHERE
table_schema='<db>'` and confirm it's empty or ours. Never flush/fake-migrate a non-empty unknown DB.
NavPMS uses its own DB **`nav_pms`**.

## L2 — Django `{# … #}` comments are single-line only
Multi-line `{# … #}` comments **leak as visible text**. Use `{% comment %} … {% endcomment %}` for any
note longer than one line. (Found in `sidebar.html` + `customizer.html` during verification.)

## L3 — HTTP-200 smoke tests miss template-comment / content leaks
A page can return 200 yet render leaked comment text or wrong content. **Pair** the status-code smoke test
(Django test client over all url names) with a **rendered-HTML content check** (assert no `{#`/`{% comment`
markers, assert expected chart/script ids and tenant name present).

## L4 — XAMPP MariaDB 10.4 vs modern Django
Django 5.1 requires MariaDB ≥ 10.5; XAMPP ships 10.4.x. Either upgrade MariaDB, pin Django 4.2 LTS, or use
a documented features shim in `config/__init__.py` (we used the shim; it disables `INSERT … RETURNING` for
MariaDB < 10.5 and relaxes the version floor).

## L6 — Stale/orphaned dev servers mask code fixes (verify via a single fresh server)
A template fix can be correct on disk + clean in `render_to_string` and the test client, yet a browser still
shows the OLD output — because a **leftover server is serving a pre-fix snapshot**. On Windows, Django
`runserver` uses `SO_REUSEADDR`, so **multiple orphaned processes can all LISTEN on the same port** (e.g. a
`preview_start` server started before the fix + `runserver` children orphaned when their wrapper task was
TaskStop'd). `Get-NetTCPConnection`/`Win32_Process` filtered by name can miss them. **Rule:** when a fix "won't
show", `netstat -ano | findstr :PORT`, kill EVERY LISTENING pid in a loop until the port is empty, `preview_stop`
any preview servers (check `preview_list`), then start ONE fresh server and re-verify over real HTTP. Then the
user must hard-refresh (Ctrl+Shift+R). The in-process test client is the authoritative render check.

## L5 — User workflow preference: fan out aggressively
The user explicitly asked to "use more Agents to complete the task as soon as possible." For large builds,
prefer a parallel multi-agent Workflow (e.g. foundation+shell in parallel, then a burst of page agents)
over a 2-agent sequential pipeline. Keep critical-path/single-writer work (migrations, shared base/static)
solo; parallelize disjoint file sets (per-app templates).

## L7 — When backend & template agents are split, PIN the detail/edit context-var name
Separate agents wrote views (`models.py`/`views.py`) and templates from a shared spec. The spec pinned the
**list** context var (`requests`, `charters`, …) but NOT the **detail/edit object** var. Result: 4/16 models
drifted — view passed `request_obj`/`business_case`/`kickoff_task`/`time_entry`, template used
`obj`/`businesscase`/`kickoff`/`timeentry` → `{% url … X.pk %}` got an empty pk → **NoReverseMatch (500)**.
**Rule:** the contract handed to parallel agents must pin EVERY context key a template consumes (detail object,
edit-mode object, every `*_choices`, every FK queryset), not just the list var. 12/16 matched only by luck
(agents independently chose the model name). The fix here was to align the view's key to the template's var.

## L8 — A GET-200 smoke test does NOT prove the page is correct (add a content assertion)
A wrong detail context var renders **blank** (Django silently swallows a missing top-level var) and still
returns 200 — only the `{% url … X.pk %}` case 500s. **Rule:** after the status-code sweep, also assert each
detail page's rendered HTML contains the object's identifier (e.g. a token from `str(obj)`); this catches the
silent-blank class. Also run the test client with `Client(raise_request_exception=False)` so one pass collects
**all** 500s instead of aborting on the first.

## L9 — Django pagination: never emit `page_obj.previous_page_number` unconditionally
`Page.previous_page_number()` / `next_page_number()` **raise `EmptyPage`** when there is no prev/next page.
Putting `…page={{ page_obj.previous_page_number }}` in a "Prev" href 500s on page 1 — but only once a list
exceeds the page size, so it's invisible with small seed data (the reference invoice list has the same latent
bug and never paginates). **Rule:** guard with `{% if page_obj.has_previous %}{{ page_obj.previous_page_number }}{% else %}1{% endif %}`
(and `has_next` / `paginator.num_pages` for Next).

## L10 — `{{ fk.get_full_name|default:fk.username|default:"—" }}` 500s when fk is None
Django swallows a failed lookup on the **main** variable, but a failed lookup in a **filter argument**
(`default:fk.username` when `fk` is None) raises `VariableDoesNotExist` and 500s. Seed data that always sets
the FK hides this. **Rule:** guard user-FK display with `{% if fk %}{{ fk.get_full_name|default:fk.username }}{% else %}—{% endif %}`.

## L11 — Integer FK list filters must validate input before `.filter(fk_id=…)`
`qs.filter(project_id=request.GET.get('project'))` raises `ValueError → 500` on non-numeric input
(`?project=abc`). Dropdowns only emit int pks, so it never shows in normal use, but a hand-edited URL hits it.
**Rule:** guard with `if value.isdigit():` (string-choice filters are immune; only int/FK params need this).

## L12 — Wire-up must come AFTER the app files exist (check-after-edit hook)
A `PostToolUse:Edit` hook runs `manage.py check` after every edit. Editing `config/urls.py`/`settings.py` to
reference a new app whose files a background workflow hasn't written yet → `No module named 'apps.<x>.urls'`
and the hook BLOCKS. **Rule:** when a build Workflow is creating the app files, do the settings/urls/navigation
wire-up as the post-build single-writer step (after the workflow completes), not concurrently. (On Modules 1–3
there was no such hook so early wire-up worked; on 4–7 it didn't.) Baking the lessons into the spec up front
(L7–L11 in `temp/specs/_conventions.md`) made the 4–7 build pass all 6 verification classes on the first pass.

## L15 — The browser caches `static/js|css` (Django dev sets no Cache-Control) → version the assets
Editing `layout.js`/`theme.css` and reloading showed NO change because the browser served the OLD file from
its HTTP cache (Django's dev static handler sends only `Last-Modified`, so browsers apply *heuristic freshness*
and skip revalidation for a while). `location.reload()` did not bust it. **Fix:** version the includes —
`<script src="{% static 'js/layout.js' %}?v=2">` (bump the number when the file changes). Then a normal reload
fetches the new URL. For verification in the preview, a unique page query (`/?_cb=<ts>`) forces a fresh HTML
fetch. (Long-term: a `{% static %}`-with-mtime template tag or ManifestStaticFilesStorage auto-versions.)

## L14 — `.claude/launch.json` runs the dev server with `--noreload` → ALWAYS restart after a build
The preview server (`launch.json` config `navpms`) starts `manage.py runserver --noreload`. `--noreload` means
**file edits are NEVER picked up** — after building/wiring a module, the running server keeps serving pre-change
code, so new sub-modules show the "On the roadmap" placeholder and edits look like they "didn't work". This is a
specific instance of [L6]. **Rule:** after finishing a module build (especially `navigation.py`/`urls.py`/
`settings.py` wiring), restart the server: find the LISTENING pid on :8000 with **`netstat -ano | Select-String
':8000\b'`** (NOT `Get-NetTCPConnection` — it false-negatived a real listener here), `Stop-Process -Id <pid>
-Force`, then `preview_start navpms`. Then verify the live page renders (fetch `/initiation/requests/` → contains
"Project Requests", not "On the roadmap"). The disk code was already correct — only the stale process was wrong.

## L13 — Template agents reference utility CSS classes that don't exist
Agents wrote `<span class="text-danger">`/`text-red` to flag negative/over-threshold values, but theme.css only
defines `.text-muted`/`.text-brand` — so the values rendered with no emphasis (cosmetic, no error). **Rule:**
define the common utilities (`.text-danger`, `.text-red`) once in theme.css's "Utility helpers" section (mirrors
`.text-muted`), with a `.dark` variant — DRY, and fixes every occurrence at once. Better: list the available
utility classes in the spec so agents don't invent class names.

## L16 — Date-equality tests flake on the UTC-offset window (use Django's `timezone`, not `datetime.date.today()`)
With `USE_TZ=True` + `TIME_ZONE='UTC'`, model/view code computes "today" as `timezone.now().date()` (the **UTC**
date). Tests that build a reference date with `datetime.date.today()` use the **local** machine date. The user is
UTC+5, so for the ~5h each morning after local midnight (local date has rolled, UTC hasn't), the two differ by
one day and any exact date-equality assertion fails — e.g. `Subscription.days_left()` returned 8 vs expected 7, and
`Invoice.paid_at == datetime.date.today()` saw UTC `06-14` vs local `06-15`. The on_stop hook (`pytest -x`) then
blocks the turn. These are **pre-existing flakes**, invisible most of the day, surfaced only by the date rollover.
**Rule:** in tests, derive the reference date from the SAME basis the code under test uses — `timezone.now().date()`
(or `timezone.localdate()`), never `datetime.date.today()` — whenever you assert exact equality against a
model/view-set date. (Two such assertions existed in `apps/tenants/tests`; fixed both.)

## L17 — A stale/half-created `test_<db>` blocks the whole suite (drop it, don't reuse)
An interrupted pytest run left `test_nav_pms` existing but without its `django_migrations` table; the next run
(reuse-db) reused the broken DB → `ProgrammingError: Table 'test_nav_pms.django_migrations' doesn't exist` /
`(1007, Can't create database 'test_nav_pms'; database exists')` in setUp, failing every test before it ran.
**Rule:** when pytest errors on the test DB itself (not an assertion), drop it and let pytest recreate clean:
`& "C:\xampp\mysql\bin\mysql.exe" -u root -h 127.0.0.1 -P 3306 -e "DROP DATABASE IF EXISTS test_nav_pms;"`
(root / no password on this XAMPP). Unrelated to app code — it's an environment reset.

## L18 — Close every module build with the specialist review agents, not just self-checks
On Modules 8-11 I verified with my own smoke test + pytest + IDOR but did NOT run the project's specialist review
agents — the user had to ask "did you run the agents?". A parallel 5-agent review (code-reviewer, security-reviewer,
performance-reviewer, frontend-reviewer, qa-smoke-tester) + adversarial verification of each finding then caught real
issues a GET-200 + content sweep CANNOT, by design: chained N+1s (a parent `__str__` resolving a 2nd FK not in
`select_related` — e.g. `Timesheet.__str__` hits `owner`, so a child list firing it per row needs
`select_related('timesheet__owner')`), a counter field (`views_count`) left writable in a ModelForm, redundant
all-one-color badge branches, and missing `<label for=>`/`id=`. None of those 500 or leak. **Rule:** the module-build
quality bar INCLUDES a closing multi-agent adversarial review as the LAST phase, run by default — not on request.
Separate the wheat from the chaff: fix defects specific to the new module; for findings that are faithful copies of
the app-wide reference pattern (non-atomic auto-numbering, global-unique numbers, missing `db_index`, filter-label
`for=`), flag an app-wide pass instead of forking one module out of step with the other ~12.

## L19 — The on_stop hook ran pytest against MySQL (shared test_nav_pms), not the SQLite test settings
This was the ROOT CAUSE of the recurring "Table 'test_nav_pms.X' doesn't exist" Stop-hook failures (the [L17]
drop-the-DB step was only a band-aid). `.claude/hooks/on_stop.py` does
`os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")` for its step-1 `manage.py check`, then spawned
`pytest` as a subprocess that INHERITED that env var. pytest-django honours the env var over `pytest.ini`, so the
hook ran the suite under `config.settings` (MySQL `nav_pms` → `test_nav_pms`) instead of the project's
`pytest.ini` default `config.settings_test` (SQLite `:memory:`). Effects: slow, MariaDB-10.4-fragile, and — when a
second session ran its suite at the same time — collisions on the shared `test_nav_pms` (half-migrated → missing
tables). My OWN `venv\Scripts\python.exe -m pytest` runs used `pytest.ini` (SQLite) and always passed, which masked
it. **Root-cause fix:** pass an explicit `env` to the pytest subprocess with
`DJANGO_SETTINGS_MODULE=config.settings_test`. Verified end-to-end: `'{}' | python .claude/hooks/on_stop.py` →
exit 0 ("manage.py check OK - tests OK") in ~70s. **Rule:** when a hook/CI runs Django tests, confirm WHICH settings
module actually resolves (env var beats `pytest.ini`); test runs must use the isolated SQLite test settings, never
the shared dev DB.

## L20 — A "masked-in-template" secret is still leaked via the edit form — EXCLUDE it from the ModelForm
Building Modules 16–20, the spec told the AutomationHook/ApiKey agents to "mask the secret in templates" AND
exclude it from the form, but the Webhook agent was only told to "mask in templates" — so `WebhookForm.fields`
kept `'secret'`. A `CharField` with no widget override renders as `<input type="text" value="{{ stored_secret }}">`
on the EDIT page, so the plaintext secret ships to the browser for any user who can open the edit form — even
though the detail page masked it with bullets. Three independent reviewers caught it; AutomationHookForm/ApiKeyForm
(same module family) already did it right by EXCLUDING the field. **Rule:** for any secret/credential/hash field,
the fix is to leave it OUT of `Meta.fields` (rotate via a dedicated write-only flow), not merely to mask it in the
detail template. Masking the read view does nothing for the bound edit form. When writing module specs, state
"exclude from the ModelForm" explicitly for every sensitive field, not "mask it".

## L21 — Verify per-module file counts after a build Workflow BEFORE wiring/migrating (workflows can be cut off mid-phase)
The 30-agent build workflow for Modules 16–20 was terminated mid-frontend-phase (parent turn interrupted), leaving
`automation` at 3/15 templates and `administration` at 14/15 while backend was 11/11 for all apps and the other three
modules were complete. A naive "workflow done → migrate + smoke test" would have hit `TemplateDoesNotExist` 500s.
**Rule:** after a code-gen Workflow, assert the expected file count per unit (e.g. `find templates/<slug> -name '*.html' | wc -l`
== 15) before relying on the output; regenerate only the missing pieces with a focused follow-up workflow. Backend
(single-writer, DB) and template (per-file) work are independent, so wiring + migrate + seed can proceed on the
complete backend while the missing templates are regenerated in parallel. Blocking on the workflow task
(`TaskOutput block=true`) also keeps a short follow-up run alive through turn boundaries.

## L22 — System-set timestamps (`*_at`) don't belong on manual edit forms (mirror finance: zero DateTimeFields on forms)
The template agents put nullable `DateTimeField` columns (`last_run_at`, `last_sync_at`, `started_at`, `recorded_at`,
`completed_at`, `last_triggered_at`) onto ModelForms with a `DateInput(type=date)` widget. That date-only widget
silently truncates the time component on every edit-save (and `datetime-local` would need matching widget+field
`input_formats` to round-trip correctly — fiddly). The finance reference puts ZERO editable DateTimeFields on its
forms — its only DateTimeFields are `auto_now`/`auto_now_add` audit columns, never in `Meta.fields`; its date widgets
sit only on real `DateField`s (issue_date/due_date/etc.). **Rule:** treat observed/system timestamps as read-only —
keep them on the model + detail page but OUT of the form. Reserve `DateInput(type=date)` for genuine user-set
`DateField`s. This is the root-cause fix, not swapping in a `datetime-local` widget.
