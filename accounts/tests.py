"""
Automated tests for accounts app: authentication, roles, workspaces, redirection, and audit events.
"""
import html
from django.contrib.auth.models import Group, Permission, User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.roles import ROLE_DEFINITIONS, setup_system_roles
from audit.models import AuditLog


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="active_user",
            password=self.password,
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username="inactive_user",
            password=self.password,
            is_active=False
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nissin Procurement")

    def test_valid_credentials_authenticate(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'active_user',
            'password': self.password,
        })
        self.assertRedirects(response, reverse('accounts:home'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_invalid_credentials_rejected(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'active_user',
            'password': 'WrongPassword999!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_inactive_user_cannot_login(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'inactive_user',
            'password': self.password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_safe_local_next_redirect(self):
        response = self.client.post(f"{reverse('accounts:login')}?next=/accounts/password-change/", {
            'username': 'active_user',
            'password': self.password,
        })
        self.assertRedirects(response, '/accounts/password-change/')

    def test_unsafe_external_next_redirect_rejected(self):
        response = self.client.post(f"{reverse('accounts:login')}?next=https://malicious-site.example.com", {
            'username': 'active_user',
            'password': self.password,
        })
        # Should fallback safely to home instead of redirecting externally
        self.assertRedirects(response, reverse('accounts:home'))

    def test_logout_requires_post_and_clears_session(self):
        self.client.login(username='active_user', password=self.password)
        # GET should be disallowed
        get_response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(get_response.status_code, 405)

        # POST logs out
        post_response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(post_response, reverse('accounts:login'))
        self.assertFalse('_auth_user_id' in self.client.session)


class RoleWorkspaceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "StrongPass123!"
        setup_system_roles()
        self.user_no_role = User.objects.create_user(
            username="norole_user",
            password=self.password
        )
        self.user_pr = User.objects.create_user(
            username="pr_user",
            password=self.password
        )
        self.group_pr = Group.objects.get(name="pr-creator")
        self.user_pr.groups.add(self.group_pr)

    def test_unauthenticated_redirected(self):
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('accounts:login')))

    def test_user_with_no_role_can_access_home(self):
        self.client.login(username='norole_user', password=self.password)
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Operational Roles Assigned")

    def test_user_can_access_assigned_workspace(self):
        self.client.login(username='pr_user', password=self.password)
        response = self.client.get(reverse('accounts:workspace', args=['pr-creator']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PR Creator")

    def test_user_cannot_access_unassigned_workspace(self):
        self.client.login(username='pr_user', password=self.password)
        # Direct URL check to an unassigned role workspace
        response = self.client.get(reverse('accounts:workspace', args=['procurement-specialist']))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Access Denied", status_code=403)


class RoleArchitectureAndRedirectionTests(TestCase):
    """
    Tests for the 10 internal system roles, setup idempotency, role-based login redirection,
    and server-side direct URL protection.
    """
    def setUp(self):
        self.client = Client()
        self.password = "Pass12345!"
        setup_system_roles()

        # Superadmin user
        self.superadmin = User.objects.create_superuser(
            username="super_test",
            password=self.password,
            email="admin@nissin.local"
        )

        # Operational users for testing
        self.user_eu = User.objects.create_user(
            username="eu_lead", password=self.password
        )
        self.user_eu.groups.add(Group.objects.get(name="enduser-maintenance-lead"))

        self.user_proc = User.objects.create_user(
            username="proc_specialist", password=self.password
        )
        self.user_proc.groups.add(Group.objects.get(name="procurement-specialist"))

        self.user_multi = User.objects.create_user(
            username="multi_role_user", password=self.password
        )
        self.user_multi.groups.add(Group.objects.get(name="odm"))
        self.user_multi.groups.add(Group.objects.get(name="procurement-site-lead"))

        self.user_none = User.objects.create_user(
            username="plain_user", password=self.password
        )

    def test_ten_internal_roles_created(self):
        """Verify exactly the 10 client-confirmed internal roles are registered."""
        expected_roles = [
            'system-administrator',
            'enduser-maintenance-lead',
            'pr-creator',
            'odm',
            'procurement-specialist',
            'procurement-site-lead',
            'laguna-manager',
            'sic-stockroom-gr-creator',
            'dct',
            'accounting-finance',
        ]
        self.assertEqual(len(ROLE_DEFINITIONS), 10)
        for role_slug in expected_roles:
            self.assertTrue(Group.objects.filter(name=role_slug).exists())
            group = Group.objects.get(name=role_slug)
            self.assertGreater(group.permissions.count(), 0)

    def test_enduser_maintenance_lead_is_single_combined_role(self):
        """Ensure End-user and Maintenance Lead are ONE combined group, not separate."""
        self.assertTrue(Group.objects.filter(name="enduser-maintenance-lead").exists())
        self.assertFalse(Group.objects.filter(name="end-user").exists())
        self.assertFalse(Group.objects.filter(name="maintenance-lead").exists())

    def test_setup_roles_is_idempotent(self):
        """Running setup_system_roles multiple times must not create duplicate groups."""
        initial_group_count = Group.objects.count()
        result = setup_system_roles()
        self.assertEqual(result['created_groups'], 0)
        self.assertEqual(Group.objects.count(), initial_group_count)

    def test_login_redirect_superadmin_to_superadmin_dashboard(self):
        """Superadmin redirects to /accounts/home/ preserving the existing Superadmin dashboard."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'super_test',
            'password': self.password,
        })
        self.assertRedirects(response, reverse('accounts:home'))

    def test_login_redirect_single_role_to_role_dashboard(self):
        """Single-role operational user redirects directly to their dashboard."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'eu_lead',
            'password': self.password,
        })
        self.assertRedirects(response, '/accounts/dashboard/enduser-maintenance-lead/')

        # Logout before logging in as another user
        self.client.logout()

        response2 = self.client.post(reverse('accounts:login'), {
            'username': 'proc_specialist',
            'password': self.password,
        })
        self.assertRedirects(response2, '/accounts/dashboard/procurement-specialist/')

    def test_login_redirect_multi_role_to_overview(self):
        """User with multiple assigned roles redirects to overview to select workspace."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'multi_role_user',
            'password': self.password,
        })
        self.assertRedirects(response, reverse('accounts:home'))

    def test_login_redirect_no_role_safely_to_home(self):
        """User with no operational role lands safely on home with unassigned message."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'plain_user',
            'password': self.password,
        })
        self.assertRedirects(response, reverse('accounts:home'))
        home_res = self.client.get(reverse('accounts:home'))
        self.assertContains(home_res, "No Operational Roles Assigned")

    def test_server_side_direct_url_protection(self):
        """Unauthorized direct URL access must be blocked with HTTP 403."""
        self.client.login(username='eu_lead', password=self.password)

        # Authorized access to own role
        res_ok = self.client.get('/accounts/dashboard/enduser-maintenance-lead/')
        self.assertEqual(res_ok.status_code, 200)
        self.assertContains(res_ok, "End-user / Maintenance Lead")

        # Unauthorized access to Laguna Manager dashboard
        res_denied = self.client.get('/accounts/dashboard/laguna-manager/')
        self.assertEqual(res_denied.status_code, 403)
        self.assertContains(res_denied, "Access Denied", status_code=403)

    def test_superadmin_can_access_all_role_dashboards(self):
        """Superadmin can inspect any dashboard without 403."""
        self.client.login(username='super_test', password=self.password)
        for slug in ROLE_DEFINITIONS.keys():
            response = self.client.get(f'/accounts/dashboard/{slug}/')
            self.assertEqual(response.status_code, 200)

    def test_all_nine_operational_dashboards_render_correctly(self):
        """Verify each of the 9 operational dashboards displays its correct role name and modules."""
        self.client.login(username='super_test', password=self.password)
        for slug, info in ROLE_DEFINITIONS.items():
            if slug == 'system-administrator':
                continue  # Preserved Superadmin dashboard
            response = self.client.get(f'/accounts/dashboard/{slug}/')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, html.escape(info['display']))
            self.assertContains(response, "Authorized Operational Modules")
            self.assertContains(response, "Confirmed Role Responsibilities")


class AuditTrailTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="audit_user",
            password=self.password
        )

    def test_login_and_logout_creates_audit_log(self):
        # Successful login
        self.client.post(reverse('accounts:login'), {
            'username': 'audit_user',
            'password': self.password,
        })
        self.assertTrue(
            AuditLog.objects.filter(event_type='LOGIN_SUCCESS', username='audit_user').exists()
        )

        # Logout
        self.client.post(reverse('accounts:logout'))
        self.assertTrue(
            AuditLog.objects.filter(event_type='LOGOUT', username='audit_user').exists()
        )

    def test_failed_login_creates_audit_log_without_password(self):
        self.client.post(reverse('accounts:login'), {
            'username': 'audit_user',
            'password': 'bad_password_to_never_store',
        })
        failed_log = AuditLog.objects.filter(event_type='LOGIN_FAILED', username='audit_user').first()
        self.assertIsNotNone(failed_log)
        # Verify raw password is not leaked in detail text
        self.assertNotIn('bad_password_to_never_store', failed_log.detail)


class VisualAndAccessibilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="ui_tester",
            password=self.password
        )

    def test_login_page_renders_logo_and_split_screen(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nissin-workspace-mark.svg")
        self.assertContains(response, "login-shell")
        self.assertContains(response, "login-aside")
        self.assertContains(response, "showPassword")
        self.assertContains(response, "skip-link")

    def test_authenticated_home_renders_workspace_branding(self):
        self.client.login(username='ui_tester', password=self.password)
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nissin-workspace-mark.svg")
        self.assertContains(response, "sidebar")
        self.assertContains(response, "topbar")
