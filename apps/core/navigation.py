"""Sidebar catalog for the Sales Management System.

`MODULE_CATALOG` mirrors SalesManagementSystem.md: 21 modules (0-20), each with five
sub-modules and a Lucide icon. `LIVE_LINKS` maps a ``(module_number, sub_module_name)``
pair to the URL name that serves it. Anything not in `LIVE_LINKS` renders as an "On the
roadmap" placeholder (``core:roadmap``) so the full product surface is visible from day one.

As future modules are built, add their sub-modules to `LIVE_LINKS` (the catalog itself
does not change). See the next-module skill.
"""
from django.urls import NoReverseMatch, reverse
from django.utils.text import slugify

MODULE_CATALOG = [
    {"number": 0, "name": "Tenant & Subscription Management", "icon": "building-2", "submodules": [
        "Tenant Onboarding", "Subscription & Billing", "Tenant Isolation & Security",
        "Custom Branding", "Tenant Health Monitoring"]},
    {"number": 1, "name": "Lead Management", "icon": "user-plus", "submodules": [
        "Lead Capture & Ingestion", "Lead Scoring & Grading", "Lead Qualification & Routing",
        "Lead Nurturing & Drip Campaigns", "Lead Conversion & Handoff"]},
    {"number": 2, "name": "Opportunity & Pipeline Management", "icon": "filter", "submodules": [
        "Opportunity Creation & Staging", "Pipeline Visibility & Forecasting",
        "Opportunity Tracking & Updates", "Competitive Intelligence",
        "Deal Collaboration & Team Selling"]},
    {"number": 3, "name": "Contact & Account Management", "icon": "contact", "submodules": [
        "Account Hierarchy & Parent-Child", "Contact Profiles & Enrichment",
        "Relationship Mapping", "Account Segmentation & Tiering",
        "Account Plans & Growth Strategies"]},
    {"number": 4, "name": "Sales Forecasting", "icon": "trending-up", "submodules": [
        "Forecast Categories & Commitments", "AI-Powered Predictive Forecasting",
        "Quota Management & Attainment", "Forecast Rollups & Adjustments",
        "Forecast Accuracy & Variance Analysis"]},
    {"number": 5, "name": "Quote & Proposal Management", "icon": "file-text", "submodules": [
        "Quote Configuration (CPQ)", "Pricing & Discount Approval",
        "Proposal Generation & Templating", "Quote Versioning & Comparison",
        "Quote-to-Order Conversion"]},
    {"number": 6, "name": "Order Management", "icon": "shopping-cart", "submodules": [
        "Order Capture & Validation", "Order Fulfillment Tracking",
        "Order Amendments & Cancellations", "Revenue Recognition & Scheduling",
        "Order History & Reorder"]},
    {"number": 7, "name": "Territory & Quota Management", "icon": "map", "submodules": [
        "Territory Design & Mapping", "Territory Assignment & Rebalancing",
        "Quota Planning & Allocation", "Coverage Model Optimization",
        "Territory Performance Analytics"]},
    {"number": 8, "name": "Sales Activity & Task Management", "icon": "list-checks", "submodules": [
        "Activity Logging & Tracking", "Task & Follow-up Management",
        "Calendar & Meeting Scheduling", "Email Integration & Tracking",
        "Daily/Weekly Sales Planning"]},
    {"number": 9, "name": "Sales Enablement", "icon": "book-open", "submodules": [
        "Content Repository & Search", "Sales Playbooks & Guidance",
        "Training & Certification Tracking", "Coaching & Call Recording",
        "Competitive Intelligence Library"]},
    {"number": 10, "name": "Incentive Compensation Management", "icon": "coins", "submodules": [
        "Commission Plan Design", "Real-Time Earnings Tracking",
        "Clawbacks & Adjustments", "Multi-Currency & Global Plans",
        "Payout Processing & Integration"]},
    {"number": 11, "name": "Customer Success & Account Management", "icon": "heart-handshake", "submodules": [
        "Health Scoring & Risk Alerts", "Renewal & Expansion Pipeline",
        "Onboarding & Implementation", "Advocacy & Reference Management",
        "Quarterly Business Reviews (QBRs)"]},
    {"number": 12, "name": "Sales Analytics & Intelligence", "icon": "bar-chart-3", "submodules": [
        "Win/Loss Analysis", "Sales Velocity & Cycle Time",
        "Conversion Funnel Analytics", "Rep Performance Scorecards",
        "Benchmarking & Peer Comparison"]},
    {"number": 13, "name": "Marketing Alignment & Attribution", "icon": "megaphone", "submodules": [
        "Campaign Influence & Attribution", "MQL-to-SQL Tracking",
        "Campaign Performance Integration", "Content Performance & Engagement",
        "Event & Webinar Management"]},
    {"number": 14, "name": "Partner & Channel Management", "icon": "handshake", "submodules": [
        "Partner Recruitment & Onboarding", "Deal Registration & Protection",
        "Partner Portal & Collaboration", "Partner Performance Tracking",
        "Channel Conflict Management"]},
    {"number": 15, "name": "Contract & Subscription Management", "icon": "scroll-text", "submodules": [
        "Contract Authoring & Redlining", "Subscription Lifecycle",
        "Renewal Automation", "Usage-Based Billing",
        "Contract Compliance & Obligations"]},
    {"number": 16, "name": "Mobile Sales", "icon": "smartphone", "submodules": [
        "Mobile CRM Access", "Field Sales Tools", "Mobile Quoting & Approvals",
        "Voice & Call Integration", "Mobile Dashboards & Alerts"]},
    {"number": 17, "name": "Workflow & Process Automation", "icon": "workflow", "submodules": [
        "Visual Process Designer", "Auto-Assignment Rules", "Approval Workflows",
        "Notification & Alert Engine", "Data Enrichment & Cleansing"]},
    {"number": 18, "name": "Integration & API Hub", "icon": "plug", "submodules": [
        "ERP Integration", "Marketing Automation", "Communication Platforms",
        "Business Intelligence", "E-Signature & Document"]},
    {"number": 19, "name": "Master Data & Configuration", "icon": "database", "submodules": [
        "Product Catalog & Pricing", "Custom Fields & Objects",
        "Sales Methodology Configuration", "User Roles & Profiles",
        "Localization & Multi-Language"]},
    {"number": 20, "name": "System Administration & Security", "icon": "shield-check", "submodules": [
        "User Management & SSO", "Data Security & Privacy", "Audit Trail & Compliance",
        "Backup & Disaster Recovery", "System Health & Performance"]},
]

# (module_number, sub_module_name) -> URL name resolved by {% url %}
LIVE_LINKS = {
    (0, "Tenant Onboarding"): "tenants:onboardingstep_list",
    (0, "Subscription & Billing"): "tenants:subscription_list",
    (0, "Tenant Isolation & Security"): "tenants:encryptionkey_list",
    (0, "Custom Branding"): "tenants:brandingsetting_list",
    (0, "Tenant Health Monitoring"): "tenants:healthmetric_list",
    # Foundation pages reachable from later modules (Master Data / Administration):
    (19, "User Roles & Profiles"): "accounts:role_list",
    (20, "User Management & SSO"): "accounts:user_list",
    (20, "Audit Trail & Compliance"): "core:audit_log",
    # Module 1 — Lead Management
    (1, "Lead Capture & Ingestion"): "leads:lead_list",
    (1, "Lead Scoring & Grading"): "leads:leadscore_list",
    (1, "Lead Qualification & Routing"): "leads:leadsource_list",
    (1, "Lead Nurturing & Drip Campaigns"): "leads:nurturecampaign_list",
    (1, "Lead Conversion & Handoff"): "leads:leadconversion_list",
    # Module 2 — Opportunity & Pipeline Management
    (2, "Opportunity Creation & Staging"): "opportunities:opportunity_list",
    (2, "Pipeline Visibility & Forecasting"): "opportunities:pipelinestage_list",
    (2, "Opportunity Tracking & Updates"): "opportunities:opportunityactivity_list",
    (2, "Competitive Intelligence"): "opportunities:competitor_list",
    (2, "Deal Collaboration & Team Selling"): "opportunities:dealcollaborator_list",
    # Module 3 — Contact & Account Management
    (3, "Account Hierarchy & Parent-Child"): "crm:account_list",
    (3, "Contact Profiles & Enrichment"): "crm:contact_list",
    (3, "Relationship Mapping"): "crm:relationshipmap_list",
    (3, "Account Segmentation & Tiering"): "crm:accounttier_list",
    (3, "Account Plans & Growth Strategies"): "crm:accountplan_list",
    # Module 4 — Sales Forecasting
    (4, "Forecast Categories & Commitments"): "forecasting:forecastcategory_list",
    (4, "AI-Powered Predictive Forecasting"): "forecasting:forecast_list",
    (4, "Quota Management & Attainment"): "forecasting:quota_list",
    (4, "Forecast Rollups & Adjustments"): "forecasting:forecastadjustment_list",
    (4, "Forecast Accuracy & Variance Analysis"): "forecasting:forecastaccuracy_list",
    # Module 5 — Quote & Proposal Management
    (5, "Quote Configuration (CPQ)"): "quotes:quote_list",
    (5, "Pricing & Discount Approval"): "quotes:pricingrule_list",
    (5, "Proposal Generation & Templating"): "quotes:proposal_list",
    (5, "Quote Versioning & Comparison"): "quotes:quoteversion_list",
    (5, "Quote-to-Order Conversion"): "quotes:quote_list",
    # Module 6 — Order Management
    (6, "Order Capture & Validation"): "orders:order_list",
    (6, "Order Fulfillment Tracking"): "orders:fulfillment_list",
    (6, "Order Amendments & Cancellations"): "orders:orderamendment_list",
    (6, "Revenue Recognition & Scheduling"): "orders:revenueschedule_list",
    (6, "Order History & Reorder"): "orders:orderline_list",
    # Module 7 — Territory & Quota Management
    (7, "Territory Design & Mapping"): "territories:territory_list",
    (7, "Territory Assignment & Rebalancing"): "territories:territoryassignment_list",
    (7, "Quota Planning & Allocation"): "territories:quotaplan_list",
    (7, "Coverage Model Optimization"): "territories:coveragemodel_list",
    (7, "Territory Performance Analytics"): "territories:territoryperformance_list",
    # Module 8 — Sales Activity & Task Management
    (8, "Activity Logging & Tracking"): "activities:activity_list",
    (8, "Task & Follow-up Management"): "activities:salestask_list",
    (8, "Calendar & Meeting Scheduling"): "activities:meeting_list",
    (8, "Email Integration & Tracking"): "activities:emaillog_list",
    (8, "Daily/Weekly Sales Planning"): "activities:salesplan_list",
    # Module 9 — Sales Enablement
    (9, "Content Repository & Search"): "enablement:contentasset_list",
    (9, "Sales Playbooks & Guidance"): "enablement:playbook_list",
    (9, "Training & Certification Tracking"): "enablement:trainingrecord_list",
    (9, "Coaching & Call Recording"): "enablement:callrecording_list",
    (9, "Competitive Intelligence Library"): "enablement:competitivecard_list",
    # Module 10 — Incentive Compensation Management
    (10, "Commission Plan Design"): "compensation:commissionplan_list",
    (10, "Real-Time Earnings Tracking"): "compensation:earning_list",
    (10, "Clawbacks & Adjustments"): "compensation:clawback_list",
    (10, "Multi-Currency & Global Plans"): "compensation:globalplanvariation_list",
    (10, "Payout Processing & Integration"): "compensation:payout_list",
    # Module 11 — Customer Success & Account Management
    (11, "Health Scoring & Risk Alerts"): "success:healthscore_list",
    (11, "Renewal & Expansion Pipeline"): "success:renewal_list",
    (11, "Onboarding & Implementation"): "success:onboardingplan_list",
    (11, "Advocacy & Reference Management"): "success:advocacy_list",
    (11, "Quarterly Business Reviews (QBRs)"): "success:qbr_list",
    # Module 12 — Sales Analytics & Intelligence
    (12, "Win/Loss Analysis"): "analytics:winlossanalysis_list",
    (12, "Sales Velocity & Cycle Time"): "analytics:salesvelocity_list",
    (12, "Conversion Funnel Analytics"): "analytics:conversionfunnel_list",
    (12, "Rep Performance Scorecards"): "analytics:repscorecard_list",
    (12, "Benchmarking & Peer Comparison"): "analytics:benchmark_list",
    # Module 13 — Marketing Alignment & Attribution
    (13, "Campaign Influence & Attribution"): "marketing:campaigninfluence_list",
    (13, "MQL-to-SQL Tracking"): "marketing:mqlhandoff_list",
    (13, "Campaign Performance Integration"): "marketing:campaignperformance_list",
    (13, "Content Performance & Engagement"): "marketing:contentengagement_list",
    (13, "Event & Webinar Management"): "marketing:marketingevent_list",
    # Module 14 — Partner & Channel Management
    (14, "Partner Recruitment & Onboarding"): "partners:partner_list",
    (14, "Deal Registration & Protection"): "partners:dealregistration_list",
    (14, "Partner Portal & Collaboration"): "partners:partnercollateral_list",
    (14, "Partner Performance Tracking"): "partners:partnerperformance_list",
    (14, "Channel Conflict Management"): "partners:channelconflict_list",
    # Module 15 — Contract & Subscription Management
    (15, "Contract Authoring & Redlining"): "contracts:contractclause_list",
    (15, "Subscription Lifecycle"): "contracts:contract_list",
    (15, "Renewal Automation"): "contracts:renewalschedule_list",
    (15, "Usage-Based Billing"): "contracts:usagerecord_list",
    (15, "Contract Compliance & Obligations"): "contracts:contractobligation_list",
    # Module 16 — Mobile Sales
    (16, "Mobile CRM Access"): "mobile:mobiledevice_list",
    (16, "Field Sales Tools"): "mobile:fieldvisit_list",
    (16, "Mobile Quoting & Approvals"): "mobile:mobilequote_list",
    (16, "Voice & Call Integration"): "mobile:callactivity_list",
    (16, "Mobile Dashboards & Alerts"): "mobile:mobilealert_list",
    # Module 17 — Workflow & Process Automation
    (17, "Visual Process Designer"): "automation:processflow_list",
    (17, "Auto-Assignment Rules"): "automation:assignmentrule_list",
    (17, "Approval Workflows"): "automation:approvalworkflow_list",
    (17, "Notification & Alert Engine"): "automation:alertrule_list",
    (17, "Data Enrichment & Cleansing"): "automation:enrichmentrule_list",
    # Module 18 — Integration & API Hub
    (18, "ERP Integration"): "integrations:connector_list",
    (18, "Marketing Automation"): "integrations:syncjob_list",
    (18, "Communication Platforms"): "integrations:synclog_list",
    (18, "Business Intelligence"): "integrations:webhook_list",
    (18, "E-Signature & Document"): "integrations:apikey_list",
    # Module 19 — Master Data & Configuration ("User Roles & Profiles" already wired above)
    (19, "Product Catalog & Pricing"): "masterdata:productcatalog_list",
    (19, "Custom Fields & Objects"): "masterdata:customfield_list",
    (19, "Sales Methodology Configuration"): "masterdata:methodologyconfig_list",
    (19, "Localization & Multi-Language"): "masterdata:localizationsetting_list",
    # Module 20 — System Administration & Security ("User Management & SSO" + "Audit Trail & Compliance" already wired above)
    (20, "Data Security & Privacy"): "administration:securitypolicy_list",
    (20, "Backup & Disaster Recovery"): "administration:backupjob_list",
    (20, "System Health & Performance"): "administration:systemhealthmetric_list",
}

_SIDEBAR_CACHE = None


def _href(module_number, sub_name):
    """Resolve a sub-module to its URL, falling back to the roadmap placeholder."""
    url_name = LIVE_LINKS.get((module_number, sub_name))
    try:
        if url_name:
            return reverse(url_name), True
        return reverse("core:roadmap", args=[module_number, slugify(sub_name)]), False
    except NoReverseMatch:
        # A live link's view isn't wired yet — degrade to the roadmap page.
        try:
            return reverse("core:roadmap", args=[module_number, slugify(sub_name)]), False
        except NoReverseMatch:
            return "#", False


def reset_sidebar_cache():
    """Drop the cached sidebar (used by tests / after wiring new LIVE_LINKS)."""
    global _SIDEBAR_CACHE
    _SIDEBAR_CACHE = None


def build_sidebar():
    """Return the resolved sidebar tree (cached after first build).

    In DEBUG we skip the cache so newly-wired LIVE_LINKS appear without a restart.
    """
    from django.conf import settings

    global _SIDEBAR_CACHE
    if _SIDEBAR_CACHE is not None and not settings.DEBUG:
        return _SIDEBAR_CACHE
    modules = []
    for mod in MODULE_CATALOG:
        subs = []
        live_count = 0
        for sub in mod["submodules"]:
            href, is_live = _href(mod["number"], sub)
            if is_live:
                live_count += 1
            subs.append({"name": sub, "href": href, "is_live": is_live})
        modules.append({
            "number": mod["number"],
            "name": mod["name"],
            "icon": mod["icon"],
            "slug": slugify(mod["name"]),
            "submodules": subs,
            "live_count": live_count,
            "total_count": len(subs),
        })
    _SIDEBAR_CACHE = modules
    return modules


def lookup_submodule(module_number, sub_slug):
    """Resolve a (module_number, sub_slug) back to display names for the roadmap page."""
    for mod in MODULE_CATALOG:
        if mod["number"] == module_number:
            for sub in mod["submodules"]:
                if slugify(sub) == sub_slug:
                    return mod["name"], sub
            return mod["name"], None
    return None, None
