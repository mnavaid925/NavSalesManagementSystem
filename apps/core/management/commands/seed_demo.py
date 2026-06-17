"""Seed core demo data: 2 tenants, roles, admins + team users, invitations.

Idempotent — safe to re-run. Run `seed_tenants` afterwards for Module 0 billing/
security/branding/health data.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Role, User, UserInvite
from apps.core.models import AuditLog, Tenant
from apps.tenants.models import OnboardingStep

PASSWORD = "password123"

TENANTS = [
    {"name": "Acme Corp", "slug": "acme", "industry": "Manufacturing"},
    {"name": "Globex Inc", "slug": "globex", "industry": "Technology"},
]

ROLES = [
    ("Administrator", Role.LEVEL_ADMIN, "Full access to the workspace."),
    ("Sales Director", Role.LEVEL_DIRECTOR, "Oversees the sales organisation."),
    ("Sales Manager", Role.LEVEL_MANAGER, "Manages a sales team."),
    ("Sales Rep", Role.LEVEL_REP, "Works leads, deals and accounts."),
]

# (first, last, role_level)
TEAM = [
    ("Sarah", "Connor", Role.LEVEL_DIRECTOR),
    ("James", "Miller", Role.LEVEL_MANAGER),
    ("Olivia", "Brown", Role.LEVEL_REP),
    ("Noah", "Smith", Role.LEVEL_REP),
]


class Command(BaseCommand):
    help = "Seed demo tenants, roles and users (idempotent)."

    def handle(self, *args, **options):
        # Platform superuser (no tenant) — for /admin only.
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@salesmanagement.local", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created superuser 'admin' / admin123 (no tenant)."))

        for spec in TENANTS:
            tenant, t_created = Tenant.objects.get_or_create(
                slug=spec["slug"],
                defaults={"name": spec["name"], "industry": spec["industry"], "status": Tenant.STATUS_ACTIVE},
            )
            if not t_created and tenant.users.exists():
                self.stdout.write(f"Tenant '{tenant.slug}' already seeded — skipping.")
                continue
            self._seed_tenant(tenant)

        self._summary()

    def _seed_tenant(self, tenant):
        roles = {}
        for name, level, desc in ROLES:
            role, _ = Role.objects.get_or_create(
                tenant=tenant, name=name, defaults={"level": level, "description": desc})
            roles[level] = role

        admin_username = f"admin_{tenant.slug}"
        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": f"admin@{tenant.slug}.example.com",
                "first_name": tenant.name.split()[0],
                "last_name": "Admin",
                "tenant": tenant,
                "role": roles[Role.LEVEL_ADMIN],
                "is_tenant_admin": True,
                "job_title": "Workspace Administrator",
            },
        )
        if created:
            admin_user.set_password(PASSWORD)
            admin_user.save()

        for first, last, level in TEAM:
            username = f"{tenant.slug}_{first.lower()}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{first.lower()}@{tenant.slug}.example.com",
                    "first_name": first, "last_name": last,
                    "tenant": tenant, "role": roles.get(level),
                    "job_title": roles.get(level).name if roles.get(level) else "",
                },
            )
            if created:
                user.set_password(PASSWORD)
                user.save()

        # A pending invitation for demonstration
        UserInvite.objects.get_or_create(
            tenant=tenant, email=f"newhire@{tenant.slug}.example.com",
            defaults={
                "role": roles.get(Role.LEVEL_REP),
                "invited_by": admin_user,
                "expires_at": timezone.now() + timedelta(days=14),
                "message": "Welcome to the team!",
            },
        )

        OnboardingStep.seed_defaults(tenant)

        if not AuditLog.objects.filter(tenant=tenant).exists():
            AuditLog.objects.create(tenant=tenant, user=admin_user, action=AuditLog.ACTION_OTHER,
                                    model_name="Tenant", object_repr=tenant.name, detail="Workspace seeded")

    def _summary(self):
        self.stdout.write(self.style.SUCCESS("\nDemo data ready."))
        self.stdout.write("Tenant admins (password: %s):" % PASSWORD)
        for spec in TENANTS:
            self.stdout.write(f"  - admin_{spec['slug']}   ({spec['name']})")
        self.stdout.write(self.style.WARNING(
            "Note: superuser 'admin' has NO tenant — module data is hidden for it by design. "
            "Log in as a tenant admin to see data."))
        self.stdout.write("Next: run  manage.py seed_tenants  for Module 0 billing/security/branding/health data.")
