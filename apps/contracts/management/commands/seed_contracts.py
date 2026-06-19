"""Seed Module 15 (Contract & Subscription Management) demo data per tenant.

Idempotent — each model is skipped if data already exists for the tenant.
Depends on `seed_demo` having created the tenants first. Safe to re-run.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.contracts.models import (
    Contract, ContractClause, ContractObligation, RenewalSchedule, UsageRecord,
)
from apps.core.models import Tenant

ACCOUNTS = [
    "Acme Corporation", "Globex Industries", "Initech Software", "Umbrella Health",
    "Stark Enterprises", "Wayne Holdings", "Wonka Beverages", "Soylent Foods",
]

OWNERS = [
    "Olivia Brown", "Noah Smith", "Sarah Connor", "James Miller",
    "Emma Davis", "Liam Wilson", "Ava Martinez",
]

CONTRACTS = [
    ("Enterprise SaaS Subscription", Contract.TYPE_NEW),
    ("Annual Renewal Agreement", Contract.TYPE_RENEWAL),
    ("Platform Amendment", Contract.TYPE_AMENDMENT),
    ("Mutual NDA", Contract.TYPE_NDA),
    ("Master Service Agreement", Contract.TYPE_MSA),
    ("Implementation SOW", Contract.TYPE_SOW),
    ("Premium Support Subscription", Contract.TYPE_NEW),
    ("Multi-Year Renewal", Contract.TYPE_RENEWAL),
]

CLAUSES = [
    ("Net-30 Payment Terms", ContractClause.TYPE_PAYMENT),
    ("Limitation of Liability", ContractClause.TYPE_LIABILITY),
    ("Termination for Convenience", ContractClause.TYPE_TERMINATION),
    ("99.9% Uptime SLA", ContractClause.TYPE_SLA),
    ("Mutual Confidentiality", ContractClause.TYPE_CONFIDENTIALITY),
    ("Auto-Renewal Terms", ContractClause.TYPE_RENEWAL),
    ("IP Ownership & License", ContractClause.TYPE_IP),
    ("Late Payment Penalty", ContractClause.TYPE_PAYMENT),
    ("Indemnification", ContractClause.TYPE_LIABILITY),
]

METRICS = [
    ("API requests", UsageRecord.UNIT_CALLS),
    ("Active seats", UsageRecord.UNIT_SEATS),
    ("Data storage", UsageRecord.UNIT_GB),
    ("Support hours", UsageRecord.UNIT_HOURS),
    ("Processed transactions", UsageRecord.UNIT_UNITS),
]

OBLIGATIONS = [
    ("Quarterly business review", ContractObligation.TYPE_DELIVERABLE),
    ("Monthly invoice payment", ContractObligation.TYPE_PAYMENT),
    ("Usage reporting", ContractObligation.TYPE_REPORTING),
    ("Uptime SLA compliance", ContractObligation.TYPE_SLA),
    ("Data protection audit", ContractObligation.TYPE_COMPLIANCE),
    ("60-day renewal notice", ContractObligation.TYPE_RENEWAL_NOTICE),
]

PERIODS = ["2026-Q1", "2026-Q2", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026"]


class Command(BaseCommand):
    help = "Seed Module 15 data (contracts, clauses, renewals, usage records, obligations)."

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        if not tenants.exists():
            self.stdout.write(self.style.WARNING("No tenants found — run `seed_demo` first."))
            return
        for tenant in tenants:
            self._seed(tenant)
        self.stdout.write(self.style.SUCCESS(
            "\nModule 15 data ready. Log in as a tenant admin to view it."))

    def _seed(self, tenant):
        today = timezone.localdate()

        # --- Contracts (parent) ---
        contracts = []
        if not Contract.objects.filter(tenant=tenant).exists():
            statuses = [Contract.STATUS_ACTIVE, Contract.STATUS_ACTIVE, Contract.STATUS_SIGNED,
                        Contract.STATUS_DRAFT, Contract.STATUS_IN_REVIEW, Contract.STATUS_SENT,
                        Contract.STATUS_EXPIRED]
            for title, ctype in CONTRACTS:
                start = today - timedelta(days=random.randint(60, 500))
                contract = Contract.objects.create(
                    tenant=tenant, title=title, account_name=random.choice(ACCOUNTS),
                    contract_type=ctype, status=random.choice(statuses),
                    value=Decimal(random.randint(20000, 500000)),
                    start_date=start,
                    end_date=start + timedelta(days=365),
                    owner=random.choice(OWNERS),
                    notes=f"{title} for the customer account.",
                )
                contracts.append(contract)
        else:
            contracts = list(Contract.objects.filter(tenant=tenant))

        # --- Contract clauses ---
        if not ContractClause.objects.filter(tenant=tenant).exists() and contracts:
            statuses = [ContractClause.STATUS_STANDARD, ContractClause.STATUS_STANDARD,
                        ContractClause.STATUS_REDLINED, ContractClause.STATUS_APPROVED,
                        ContractClause.STATUS_REJECTED]
            risks = [c[0] for c in ContractClause.RISK_LEVEL_CHOICES]
            chosen = random.sample(CLAUSES, k=random.randint(6, len(CLAUSES)))
            for title, ctype in chosen:
                ContractClause.objects.create(
                    tenant=tenant, contract=random.choice(contracts),
                    title=title, clause_type=ctype,
                    status=random.choice(statuses), risk_level=random.choice(risks),
                    body=f"{title}: standard contractual language governing this clause.",
                    notes="Reviewed by legal.",
                )

        # --- Renewal schedules ---
        if not RenewalSchedule.objects.filter(tenant=tenant).exists() and contracts:
            statuses = [RenewalSchedule.STATUS_UPCOMING, RenewalSchedule.STATUS_IN_PROGRESS,
                        RenewalSchedule.STATUS_RENEWED, RenewalSchedule.STATUS_AT_RISK,
                        RenewalSchedule.STATUS_CHURNED]
            for i in range(random.randint(6, 9)):
                contract = random.choice(contracts)
                current = Decimal(random.randint(20000, 300000))
                proposed = (current * Decimal(str(round(random.uniform(0.9, 1.3), 2)))
                            ).quantize(Decimal("0.01"))
                RenewalSchedule.objects.create(
                    tenant=tenant, contract=contract, account_name=contract.account_name,
                    status=random.choice(statuses),
                    renewal_date=today + timedelta(days=random.randint(15, 240)),
                    current_value=current, proposed_value=proposed,
                    auto_renew=random.choice([True, False]),
                    notice_days=random.choice([30, 45, 60, 90]),
                    notes="Renewal tracked for upcoming term.",
                )

        # --- Usage records ---
        if not UsageRecord.objects.filter(tenant=tenant).exists() and contracts:
            for i in range(random.randint(8, 12)):
                contract = random.choice(contracts)
                metric, unit = random.choice(METRICS)
                quantity = Decimal(random.randint(100, 50000))
                rate = Decimal(str(round(random.uniform(0.05, 12.50), 4)))
                amount = (quantity * rate).quantize(Decimal("0.01"))
                UsageRecord.objects.create(
                    tenant=tenant, contract=contract, account_name=contract.account_name,
                    metric_name=metric, quantity=quantity, unit=unit,
                    rate=rate, amount=amount, period_label=random.choice(PERIODS),
                    recorded_on=today - timedelta(days=random.randint(1, 120)),
                )

        # --- Contract obligations ---
        if not ContractObligation.objects.filter(tenant=tenant).exists() and contracts:
            statuses = [ContractObligation.STATUS_PENDING, ContractObligation.STATUS_IN_PROGRESS,
                        ContractObligation.STATUS_MET, ContractObligation.STATUS_MISSED,
                        ContractObligation.STATUS_WAIVED]
            for i in range(random.randint(6, 10)):
                contract = random.choice(contracts)
                title, otype = random.choice(OBLIGATIONS)
                ContractObligation.objects.create(
                    tenant=tenant, contract=contract, title=title,
                    obligation_type=otype, status=random.choice(statuses),
                    due_date=today + timedelta(days=random.randint(-30, 180)),
                    owner=random.choice(OWNERS),
                    notes="Obligation tracked for compliance.",
                )

        self.stdout.write(f"  seeded Module 15 data for '{tenant.slug}'")
