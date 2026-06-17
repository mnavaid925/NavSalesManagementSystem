## dump_module.ps1
##
## Generates a consolidated <NN>_<slug>.txt file in temp/ containing all backend
## (apps/<name>/) and frontend (templates/<name>/) code for one NavPMS module.
##
## NavPMS is a multi-tenant Project Management System (Django 5.1 + Tailwind/HTMX/Chart.js/Lucide,
## MySQL/MariaDB via PyMySQL). Module 0 (apps/tenants) is the flagship COMPLETE module; the
## foundation apps accounts/core/projects/dashboard are also built. Modules 1-20 are roadmap
## placeholders built on demand by the /next-module skill — until then the script prints
## "(no backend folder found ...)" for them, which is expected.
##
## Usage:
##   pwsh .claude\skills\dump-module\dump_module.ps1 -Module tenants
##   pwsh .claude\skills\dump-module\dump_module.ps1 -Module 0
##   pwsh .claude\skills\dump-module\dump_module.ps1 -Module "projects"
##   pwsh .claude\skills\dump-module\dump_module.ps1 -Module all      # regenerates every module

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Module,

    [string]$RepoRoot = 'C:\xampp\htdocs\NavProjectManagementSystem'
)

$ErrorActionPreference = 'Stop'

# -------- Module registry --------
# key = output file slug; value = @(<apps_folder>, <templates_folder>, <human title>)
# Built today: tenants (Module 0) + the foundation apps accounts/core/projects/dashboard.
# Modules 1-20 are FORWARD-COMPATIBLE entries matching the /next-module roadmap app slugs;
# their apps/<slug> + templates/<slug> folders do not exist until /next-module builds them.
$registry = [ordered]@{
    # --- Module 0 (COMPLETE) + foundation apps ---
    '00_tenant_subscription_management' = @('tenants',        'tenants',        '0. Tenant & Subscription Management')
    'accounts'                          = @('accounts',       'accounts',       'Foundation: Accounts (Users, Roles, Auth)')
    'core'                              = @('core',           'core',           'Foundation: Core (Tenant, Audit, Navigation)')
    'projects'                          = @('projects',       'projects',       'Foundation: Workspace (Projects, Tasks, Meetings, Tickets, Invoices)')
    'dashboard'                         = @('dashboard',      'dashboard',      'Foundation: Dashboard (KPI aggregation)')
    # --- Modules 1-20 (roadmap; built on demand by /next-module) ---
    '01_project_initiation'             = @('initiation',     'initiation',     '1. Project Initiation & Charter')
    '02_project_planning'               = @('planning',       'planning',       '2. Project Planning & Scheduling')
    '03_resource_management'            = @('resources',      'resources',      '3. Resource Management')
    '04_cost_budget_management'         = @('budgeting',      'budgeting',      '4. Cost & Budget Management')
    '05_risk_issue_management'          = @('risks',          'risks',          '5. Risk & Issue Management')
    '06_quality_management'             = @('quality',        'quality',        '6. Quality Management')
    '07_scope_requirements'             = @('scope',          'scope',          '7. Scope & Requirements Management')
    '08_task_work_management'           = @('work',           'work',           '8. Task & Work Management')
    '09_collaboration'                  = @('collaboration',  'collaboration',  '9. Collaboration & Communication')
    '10_document_knowledge'             = @('documents',      'documents',      '10. Document & Knowledge Management')
    '11_time_attendance'                = @('timesheets',     'timesheets',     '11. Time & Attendance Tracking')
    '12_portfolio_program'              = @('portfolio',      'portfolio',      '12. Portfolio & Program Management')
    '13_agile_scrum'                    = @('agile',          'agile',          '13. Agile & Scrum Management')
    '14_client_collaboration'           = @('clients',        'clients',        '14. Client & External Collaboration')
    '15_financial_billing'              = @('finance',        'finance',        '15. Financial & Billing Management')
    '16_reporting_bi'                   = @('reporting',      'reporting',      '16. Reporting & Business Intelligence')
    '17_workflow_automation'            = @('automation',     'automation',     '17. Workflow & Automation')
    '18_integration_api'                = @('integrations',   'integrations',   '18. Integration & API Hub')
    '19_master_data'                    = @('masterdata',     'masterdata',     '19. Master Data & Configuration')
    '20_system_administration'          = @('administration', 'administration', '20. System Administration & Security')
}

# Friendly aliases -> registry key
$aliases = @{
    # --- Module 0 + foundation ---
    '0'   = '00_tenant_subscription_management'
    '00'  = '00_tenant_subscription_management'
    'tenants'        = '00_tenant_subscription_management'
    'tenant'         = '00_tenant_subscription_management'
    'subscription'   = '00_tenant_subscription_management'
    'subscriptions'  = '00_tenant_subscription_management'
    'billing'        = '00_tenant_subscription_management'
    'accounts'       = 'accounts'
    'account'        = 'accounts'
    'users'          = 'accounts'
    'user'           = 'accounts'
    'roles'          = 'accounts'
    'auth'           = 'accounts'
    'core'           = 'core'
    'audit'          = 'core'
    'navigation'     = 'core'
    'projects'       = 'projects'
    'project'        = 'projects'
    'workspace'      = 'projects'
    'tasks'          = 'projects'
    'meetings'       = 'projects'
    'tickets'        = 'projects'
    'dashboard'      = 'dashboard'
    'kpi'            = 'dashboard'
    'home'           = 'dashboard'
    # --- Modules 1-20 numeric ---
    '1'   = '01_project_initiation'
    '01'  = '01_project_initiation'
    '2'   = '02_project_planning'
    '02'  = '02_project_planning'
    '3'   = '03_resource_management'
    '03'  = '03_resource_management'
    '4'   = '04_cost_budget_management'
    '04'  = '04_cost_budget_management'
    '5'   = '05_risk_issue_management'
    '05'  = '05_risk_issue_management'
    '6'   = '06_quality_management'
    '06'  = '06_quality_management'
    '7'   = '07_scope_requirements'
    '07'  = '07_scope_requirements'
    '8'   = '08_task_work_management'
    '08'  = '08_task_work_management'
    '9'   = '09_collaboration'
    '09'  = '09_collaboration'
    '10'  = '10_document_knowledge'
    '11'  = '11_time_attendance'
    '12'  = '12_portfolio_program'
    '13'  = '13_agile_scrum'
    '14'  = '14_client_collaboration'
    '15'  = '15_financial_billing'
    '16'  = '16_reporting_bi'
    '17'  = '17_workflow_automation'
    '18'  = '18_integration_api'
    '19'  = '19_master_data'
    '20'  = '20_system_administration'
    # --- Modules 1-20 app folder names + friendly keywords ---
    'initiation'     = '01_project_initiation'
    'charter'        = '01_project_initiation'
    'planning'       = '02_project_planning'
    'scheduling'     = '02_project_planning'
    'wbs'            = '02_project_planning'
    'resources'      = '03_resource_management'
    'resource'       = '03_resource_management'
    'allocation'     = '03_resource_management'
    'budgeting'      = '04_cost_budget_management'
    'budget'         = '04_cost_budget_management'
    'cost'           = '04_cost_budget_management'
    'risks'          = '05_risk_issue_management'
    'risk'           = '05_risk_issue_management'
    'issues'         = '05_risk_issue_management'
    'quality'        = '06_quality_management'
    'qa'             = '06_quality_management'
    'scope'          = '07_scope_requirements'
    'requirements'   = '07_scope_requirements'
    'work'           = '08_task_work_management'
    'kanban'         = '08_task_work_management'
    'collaboration'  = '09_collaboration'
    'communication'  = '09_collaboration'
    'documents'      = '10_document_knowledge'
    'document'       = '10_document_knowledge'
    'knowledge'      = '10_document_knowledge'
    'timesheets'     = '11_time_attendance'
    'timesheet'      = '11_time_attendance'
    'attendance'     = '11_time_attendance'
    'portfolio'      = '12_portfolio_program'
    'program'        = '12_portfolio_program'
    'agile'          = '13_agile_scrum'
    'scrum'          = '13_agile_scrum'
    'sprint'         = '13_agile_scrum'
    'clients'        = '14_client_collaboration'
    'client'         = '14_client_collaboration'
    'finance'        = '15_financial_billing'
    'financial'      = '15_financial_billing'
    'reporting'      = '16_reporting_bi'
    'reports'        = '16_reporting_bi'
    'bi'             = '16_reporting_bi'
    'automation'     = '17_workflow_automation'
    'workflow'       = '17_workflow_automation'
    'integrations'   = '18_integration_api'
    'integration'    = '18_integration_api'
    'api'            = '18_integration_api'
    'masterdata'     = '19_master_data'
    'configuration'  = '19_master_data'
    'config'         = '19_master_data'
    'administration' = '20_system_administration'
    'admin'          = '20_system_administration'
    'security'       = '20_system_administration'
}

# -------- Resolve which keys to process --------
$targetKeys = @()
$lookup = $Module.Trim().ToLower()

if ($lookup -eq 'all' -or $lookup -eq '*') {
    $targetKeys = @($registry.Keys)
}
elseif ($registry.Contains($Module)) {
    $targetKeys = @($Module)
}
elseif ($aliases.ContainsKey($lookup)) {
    $targetKeys = @($aliases[$lookup])
}
else {
    # last-chance fuzzy: contains match against title
    foreach ($k in $registry.Keys) {
        $title = $registry[$k][2].ToLower()
        if ($title -like "*$lookup*") {
            $targetKeys = @($k)
            break
        }
    }
}

if ($targetKeys.Count -eq 0) {
    Write-Error @"
Unknown module: '$Module'.

Valid identifiers:
  Number:       0..20  (or 00..20)
  App folder:   tenants, accounts, core, projects, dashboard,
                initiation, planning, resources, budgeting, risks, quality, scope, work,
                collaboration, documents, timesheets, portfolio, agile, clients, finance,
                reporting, automation, integrations, masterdata, administration
  Special:      all   (regenerate every module)

Examples:
  pwsh .claude\skills\dump-module\dump_module.ps1 -Module tenants
  pwsh .claude\skills\dump-module\dump_module.ps1 -Module 0
  pwsh .claude\skills\dump-module\dump_module.ps1 -Module projects
  pwsh .claude\skills\dump-module\dump_module.ps1 -Module all
"@
    exit 1
}

# -------- Ensure temp/ exists --------
$outDir = Join-Path $RepoRoot 'temp'
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

# -------- Helpers --------
function Add-Section {
    param([string]$OutFile, [string]$Header)
    $banner = ('=' * 100)
    Add-Content -Path $OutFile -Value "`r`n$banner`r`n$Header`r`n$banner`r`n" -Encoding UTF8
}

function Add-FileBlock {
    param([string]$OutFile, [System.IO.FileInfo]$File, [string]$RelPath)
    $sub = ('-' * 100)
    Add-Content -Path $OutFile -Value "`r`n$sub`r`nFILE: $RelPath`r`n$sub" -Encoding UTF8
    $content = [System.IO.File]::ReadAllText($File.FullName)
    Add-Content -Path $OutFile -Value $content -Encoding UTF8
}

# -------- Generate --------
foreach ($key in $targetKeys) {
    $appsFolder, $tplFolder, $title = $registry[$key]
    $outFile = Join-Path $outDir "$key.txt"

    Set-Content -Path $outFile -Value "" -Encoding UTF8

    $banner = ('#' * 100)
    Add-Content -Path $outFile -Value "$banner`r`n# MODULE $title`r`n# Backend:  apps\$appsFolder\`r`n# Frontend: templates\$tplFolder\`r`n# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`r`n$banner" -Encoding UTF8

    # Backend
    $appsPath = Join-Path $RepoRoot "apps\$appsFolder"
    if (Test-Path $appsPath) {
        Add-Section -OutFile $outFile -Header "BACKEND  (apps\$appsFolder\)"
        $files = Get-ChildItem -Path $appsPath -Recurse -File `
            | Where-Object { $_.FullName -notmatch '__pycache__' } `
            | Where-Object { $_.Extension -in '.py', '.txt', '.md', '.json', '.yml', '.yaml', '.cfg', '.ini' } `
            | Sort-Object FullName
        foreach ($f in $files) {
            $rel = $f.FullName.Substring($RepoRoot.Length + 1)
            Add-FileBlock -OutFile $outFile -File $f -RelPath $rel
        }
    } else {
        Add-Content -Path $outFile -Value "`r`n(no backend folder found at apps\$appsFolder\)`r`n" -Encoding UTF8
    }

    # Frontend
    $tplPath = Join-Path $RepoRoot "templates\$tplFolder"
    if (Test-Path $tplPath) {
        Add-Section -OutFile $outFile -Header "FRONTEND  (templates\$tplFolder\)"
        $files = Get-ChildItem -Path $tplPath -Recurse -File `
            | Where-Object { $_.Extension -in '.html', '.htm', '.js', '.css', '.txt' } `
            | Sort-Object FullName
        foreach ($f in $files) {
            $rel = $f.FullName.Substring($RepoRoot.Length + 1)
            Add-FileBlock -OutFile $outFile -File $f -RelPath $rel
        }
    } else {
        Add-Content -Path $outFile -Value "`r`n(no frontend folder found at templates\$tplFolder\)`r`n" -Encoding UTF8
    }

    $size = (Get-Item $outFile).Length
    Write-Output ("OK  {0,-45} {1,12:N0} bytes  ->  temp\{0}.txt" -f $key, $size)
}
