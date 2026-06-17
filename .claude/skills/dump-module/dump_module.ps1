## dump_module.ps1
##
## Generates a consolidated <NN>_<slug>.txt file in temp/ containing all backend
## (apps/<name>/) and frontend (templates/<name>/) code for one NavSalesManagementSystem module.
##
## NavSalesManagementSystem is a multi-tenant Sales Management System (Django 5.1 + Tailwind/HTMX/Chart.js/Lucide,
## MySQL/MariaDB via PyMySQL, DB nav_sms). Module 0 (apps/tenants) is the flagship COMPLETE module; the
## foundation apps accounts/core/dashboard are also built. Modules 1-20 are roadmap
## placeholders built on demand by the /next-module skill — until then the script prints
## "(no backend folder found ...)" for them, which is expected.
##
## Usage:
##   pwsh .claude\skills\dump-module\dump_module.ps1 -Module tenants
##   pwsh .claude\skills\dump-module\dump_module.ps1 -Module 0
##   pwsh .claude\skills\dump-module\dump_module.ps1 -Module "leads"
##   pwsh .claude\skills\dump-module\dump_module.ps1 -Module all      # regenerates every module

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Module,

    [string]$RepoRoot = 'C:\xampp\htdocs\NavSalesManagementSystem'
)

$ErrorActionPreference = 'Stop'

# -------- Module registry --------
# key = output file slug; value = @(<apps_folder>, <templates_folder>, <human title>)
# Built today: tenants (Module 0) + the foundation apps accounts/core/dashboard.
# Modules 1-20 are FORWARD-COMPATIBLE entries matching the /next-module roadmap app slugs;
# their apps/<slug> + templates/<slug> folders do not exist until /next-module builds them.
$registry = [ordered]@{
    # --- Module 0 (COMPLETE) + foundation apps ---
    '00_tenants'        = @('tenants',        'tenants',        '0. Tenant & Subscription Management')
    'accounts'          = @('accounts',       'accounts',       'Foundation: Accounts (Users, Roles, Auth)')
    'core'              = @('core',           'core',           'Foundation: Core (Tenant, Audit, Navigation)')
    'dashboard'         = @('dashboard',      'dashboard',      'Foundation: Dashboard (KPI aggregation)')
    # --- Modules 1-20 (roadmap; built on demand by /next-module) ---
    '01_leads'          = @('leads',          'leads',          '1. Lead Management')
    '02_opportunities'  = @('opportunities',  'opportunities',  '2. Opportunity & Pipeline Management')
    '03_crm'            = @('crm',            'crm',            '3. Contact & Account Management')
    '04_forecasting'    = @('forecasting',    'forecasting',    '4. Sales Forecasting')
    '05_quotes'         = @('quotes',         'quotes',         '5. Quote & Proposal Management')
    '06_orders'         = @('orders',         'orders',         '6. Order Management')
    '07_territories'    = @('territories',    'territories',    '7. Territory & Quota Management')
    '08_activities'     = @('activities',     'activities',     '8. Sales Activity & Task Management')
    '09_enablement'     = @('enablement',     'enablement',     '9. Sales Enablement')
    '10_compensation'   = @('compensation',   'compensation',   '10. Incentive Compensation Management')
    '11_success'        = @('success',        'success',        '11. Customer Success & Account Management')
    '12_analytics'      = @('analytics',      'analytics',      '12. Sales Analytics & Intelligence')
    '13_marketing'      = @('marketing',      'marketing',      '13. Marketing Alignment & Attribution')
    '14_partners'       = @('partners',       'partners',       '14. Partner & Channel Management')
    '15_contracts'      = @('contracts',      'contracts',      '15. Contract & Subscription Management')
    '16_mobile'         = @('mobile',         'mobile',         '16. Mobile Sales')
    '17_automation'     = @('automation',     'automation',     '17. Workflow & Process Automation')
    '18_integrations'   = @('integrations',   'integrations',   '18. Integration & API Hub')
    '19_masterdata'     = @('masterdata',     'masterdata',     '19. Master Data & Configuration')
    '20_administration' = @('administration', 'administration', '20. System Administration & Security')
}

# Friendly aliases -> registry key
$aliases = @{
    # --- Module 0 + foundation ---
    '0'   = '00_tenants'
    '00'  = '00_tenants'
    'tenants'        = '00_tenants'
    'tenant'         = '00_tenants'
    'subscription'   = '00_tenants'
    'subscriptions'  = '00_tenants'
    'billing'        = '00_tenants'
    'invoice'        = '00_tenants'
    'invoices'       = '00_tenants'
    'accounts'       = 'accounts'
    'account'        = 'accounts'
    'users'          = 'accounts'
    'user'           = 'accounts'
    'roles'          = 'accounts'
    'auth'           = 'accounts'
    'core'           = 'core'
    'audit'          = 'core'
    'navigation'     = 'core'
    'dashboard'      = 'dashboard'
    'kpi'            = 'dashboard'
    'home'           = 'dashboard'
    # --- Modules 1-20 numeric ---
    '1'   = '01_leads'
    '01'  = '01_leads'
    '2'   = '02_opportunities'
    '02'  = '02_opportunities'
    '3'   = '03_crm'
    '03'  = '03_crm'
    '4'   = '04_forecasting'
    '04'  = '04_forecasting'
    '5'   = '05_quotes'
    '05'  = '05_quotes'
    '6'   = '06_orders'
    '06'  = '06_orders'
    '7'   = '07_territories'
    '07'  = '07_territories'
    '8'   = '08_activities'
    '08'  = '08_activities'
    '9'   = '09_enablement'
    '09'  = '09_enablement'
    '10'  = '10_compensation'
    '11'  = '11_success'
    '12'  = '12_analytics'
    '13'  = '13_marketing'
    '14'  = '14_partners'
    '15'  = '15_contracts'
    '16'  = '16_mobile'
    '17'  = '17_automation'
    '18'  = '18_integrations'
    '19'  = '19_masterdata'
    '20'  = '20_administration'
    # --- Modules 1-20 app folder names + friendly keywords (sales terms) ---
    'leads'          = '01_leads'
    'lead'           = '01_leads'
    'nurture'        = '01_leads'
    'opportunities'  = '02_opportunities'
    'opportunity'    = '02_opportunities'
    'pipeline'       = '02_opportunities'
    'deal'           = '02_opportunities'
    'deals'          = '02_opportunities'
    'crm'            = '03_crm'
    'contact'        = '03_crm'
    'contacts'       = '03_crm'
    'forecasting'    = '04_forecasting'
    'forecast'       = '04_forecasting'
    'quota'          = '04_forecasting'
    'quotes'         = '05_quotes'
    'quote'          = '05_quotes'
    'proposal'       = '05_quotes'
    'cpq'            = '05_quotes'
    'orders'         = '06_orders'
    'order'          = '06_orders'
    'fulfillment'    = '06_orders'
    'territories'    = '07_territories'
    'territory'      = '07_territories'
    'activities'     = '08_activities'
    'activity'       = '08_activities'
    'task'           = '08_activities'
    'tasks'          = '08_activities'
    'enablement'     = '09_enablement'
    'playbook'       = '09_enablement'
    'training'       = '09_enablement'
    'compensation'   = '10_compensation'
    'commission'     = '10_compensation'
    'incentive'      = '10_compensation'
    'payout'         = '10_compensation'
    'success'        = '11_success'
    'renewal'        = '11_success'
    'qbr'            = '11_success'
    'analytics'      = '12_analytics'
    'intelligence'   = '12_analytics'
    'velocity'       = '12_analytics'
    'marketing'      = '13_marketing'
    'campaign'       = '13_marketing'
    'attribution'    = '13_marketing'
    'partners'       = '14_partners'
    'partner'        = '14_partners'
    'channel'        = '14_partners'
    'contracts'      = '15_contracts'
    'contract'       = '15_contracts'
    'mobile'         = '16_mobile'
    'field'          = '16_mobile'
    'automation'     = '17_automation'
    'workflow'       = '17_automation'
    'process'        = '17_automation'
    'integrations'   = '18_integrations'
    'integration'    = '18_integrations'
    'api'            = '18_integrations'
    'connector'      = '18_integrations'
    'masterdata'     = '19_masterdata'
    'configuration'  = '19_masterdata'
    'config'         = '19_masterdata'
    'catalog'        = '19_masterdata'
    'product'        = '19_masterdata'
    'administration' = '20_administration'
    'admin'          = '20_administration'
    'security'       = '20_administration'
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
  App folder:   tenants, accounts, core, dashboard,
                leads, opportunities, crm, forecasting, quotes, orders, territories,
                activities, enablement, compensation, success, analytics, marketing,
                partners, contracts, mobile, automation, integrations, masterdata, administration
  Special:      all   (regenerate every module)

Examples:
  pwsh .claude\skills\dump-module\dump_module.ps1 -Module tenants
  pwsh .claude\skills\dump-module\dump_module.ps1 -Module 0
  pwsh .claude\skills\dump-module\dump_module.ps1 -Module leads
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
