from django.contrib import admin

from .models import (
    Contract, ContractClause, ContractObligation, RenewalSchedule, UsageRecord,
)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "title", "account_name", "contract_type", "status", "value", "start_date")
    list_filter = ("tenant", "contract_type", "status")
    search_fields = ("number", "title", "account_name", "owner")
    readonly_fields = ("number",)


@admin.register(ContractClause)
class ContractClauseAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "contract", "clause_type", "status", "risk_level")
    list_filter = ("tenant", "clause_type", "status", "risk_level")
    search_fields = ("title", "body", "notes")


@admin.register(RenewalSchedule)
class RenewalScheduleAdmin(admin.ModelAdmin):
    list_display = ("account_name", "tenant", "contract", "status", "renewal_date", "current_value", "auto_renew")
    list_filter = ("tenant", "status", "auto_renew")
    search_fields = ("account_name", "notes")


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("metric_name", "tenant", "account_name", "contract", "quantity", "unit", "amount", "recorded_on")
    list_filter = ("tenant", "unit")
    search_fields = ("account_name", "metric_name", "period_label")


@admin.register(ContractObligation)
class ContractObligationAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "contract", "obligation_type", "status", "due_date", "owner")
    list_filter = ("tenant", "obligation_type", "status")
    search_fields = ("title", "owner", "notes")
