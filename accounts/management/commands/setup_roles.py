"""
Management command to set up the 10 internal system roles and permissions.

This command is idempotent — safe to run multiple times.
It will NOT remove existing groups or users.
It creates the groups and assigns the confirmed operational permissions.

Usage:
    python manage.py setup_roles
"""
from django.core.management.base import BaseCommand
from accounts.roles import setup_system_roles, ROLE_DEFINITIONS


class Command(BaseCommand):
    help = 'Create the ten internal system roles and assign confirmed permissions (idempotent).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Setting up Nissin internal system roles...'))

        result = setup_system_roles()

        for slug, info in ROLE_DEFINITIONS.items():
            perm_count = len(info.get('permissions', []))
            self.stdout.write(self.style.SUCCESS(
                f"  - [{slug}] {info['display']}: {perm_count} operational permissions assigned"
            ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f"Role setup complete. Total roles: {result['total_roles']} "
            f"(Created: {result['created_groups']}, Existing: {result['existing_groups']}, "
            f"Permissions registered: {result['created_permissions']})"
        ))
