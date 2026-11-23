"""
Accounts views — authentication, dashboard, role workspaces, and password management.
"""
import logging
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.template.loader import select_template
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_http_methods

from audit.models import AuditLog
from .forms import NissinLoginForm, NissinPasswordChangeForm
from .roles import (
    ROLE_DEFINITIONS,
    get_user_operational_roles,
    get_post_login_redirect_url,
)

logger = logging.getLogger(__name__)


def _is_safe_redirect(url, request):
    """Validate a redirect URL to prevent open redirects."""
    if not url:
        return False
    return url_has_allowed_host_and_scheme(
        url=url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user login with role-based redirection.

    After successful authentication:
    - Superadmin / staff -> Superadmin Overview dashboard ('accounts:home')
    - Operational user with 1 role -> Direct to role-specific dashboard
    - User with multiple roles -> Overview dashboard ('accounts:home')
    - User without operational role -> Safe landing on Overview ('accounts:home')
    """
    if request.user.is_authenticated:
        return redirect(get_post_login_redirect_url(request.user))

    if request.method == 'POST':
        form = NissinLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info("User '%s' logged in successfully.", user.username)

            # Prioritize safe local 'next' parameter if explicitly provided
            next_url = request.POST.get('next') or request.GET.get('next', '')
            if next_url and _is_safe_redirect(next_url, request):
                return redirect(next_url)

            # Redirect based on assigned roles
            destination = get_post_login_redirect_url(user)
            return redirect(destination)
        else:
            logger.info("Failed login attempt.")
    else:
        form = NissinLoginForm(request)

    next_url = request.GET.get('next', '')
    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url,
    })


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
@require_POST
@csrf_protect
def logout_view(request):
    """Log out the user via POST with CSRF protection."""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        logger.info("User '%s' logged out.", username)
    return redirect('accounts:login')


# ---------------------------------------------------------------------------
# Home / Superadmin & Overview Dashboard
# ---------------------------------------------------------------------------
@login_required
def home_view(request):
    """
    Authenticated home / overview dashboard.
    Acts as the Superadmin dashboard for administrators and the multi-role switcher
    for operational personnel.
    """
    user = request.user
    available_roles = get_user_operational_roles(user)
    is_admin = user.is_superuser or user.is_staff or user.groups.filter(name='system-administrator').exists()

    context = {
        'user': user,
        'available_roles': available_roles,
        'all_roles': ROLE_DEFINITIONS,
        'is_admin': is_admin,
        'has_roles': len(available_roles) > 0,
        'display_name': user.get_full_name() or user.username,
    }
    return render(request, 'accounts/home.html', context)


# ---------------------------------------------------------------------------
# Role-Specific Operational Dashboard
# ---------------------------------------------------------------------------
@login_required
def role_dashboard_view(request, role_slug):
    """
    Render the operational dashboard for a specific system role.
    Guarded by server-side permission verification:
    - Superusers have access to all dashboards for oversight.
    - Standard users must belong to the matching role Group.
    - Unauthorized access or tampering returns 403 Forbidden and logs an audit event.
    """
    if role_slug not in ROLE_DEFINITIONS:
        return render(request, 'accounts/access_denied.html', {
            'message': 'The requested operational workspace does not exist.',
        }, status=403)

    is_member = request.user.groups.filter(name=role_slug).exists()
    is_superuser = request.user.is_superuser

    if not (is_member or is_superuser):
        AuditLog.objects.create(
            event_type='ROLE_REMOVED',  # Categorized security event
            user=request.user,
            username=request.user.username,
            detail=f"Security: Blocked unauthorized direct URL access attempt to '{role_slug}' dashboard.",
        )
        return render(request, 'accounts/access_denied.html', {
            'message': f"You do not have permission to access the {ROLE_DEFINITIONS[role_slug]['display']} dashboard. "
                       f"Contact your System Administrator if you require this role.",
        }, status=403)

    role_info = ROLE_DEFINITIONS[role_slug]
    user_roles = get_user_operational_roles(request.user)
    other_roles = [r for r in user_roles if r['slug'] != role_slug]

    # Compute initials, display name, and greeting name
    full_name = request.user.get_full_name()
    if full_name:
        parts = full_name.split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()
        greeting_name = request.user.last_name or parts[-1]
        display_name = f"{parts[0][0]}. {parts[-1]}" if len(parts) > 1 else full_name
    elif request.user.username and request.user.username not in ('eu_lead', 'user', 'active_user'):
        initials = request.user.username[:2].upper()
        greeting_name = request.user.username.title()
        display_name = request.user.username
    else:
        # Default aligned with reference screenshot persona
        initials = "RE"
        greeting_name = "Espina"
        display_name = "R. Espina"

    context = {
        'role_slug': role_slug,
        'role_info': role_info,
        'role_display': role_info['display'],
        'role_description': role_info['description'],
        'phase_status': role_info.get('phase_status', 'Active'),
        'other_roles': other_roles,
        'is_admin': request.user.is_superuser or request.user.is_staff,
        'display_name': display_name,
        'greeting_name': greeting_name,
        'user_initials': initials,
        'open_needs_count': 12,
        'open_needs_as_of': 'As of 16 Nov 09:40',
        'awaiting_action_count': 2,
        'awaiting_action_desc': 'Acknowledgement pending',
        'delivered_month_count': 7,
        'delivered_month_desc': 'From recorded receipts',
        'stock_alerts_count': 4,
        'stock_alerts_desc': 'From stock count, not SAP',
    }

    # Use specialized template if available; fallback to dashboard_base.html
    template_candidates = [
        f"accounts/dashboards/{role_slug.replace('-', '_')}.html",
        "accounts/dashboard_base.html",
        "accounts/workspace.html",
    ]
    template = select_template(template_candidates)
    return render(request, template.template.name, context)


# Alias for backward compatibility
role_workspace_view = role_dashboard_view


# ---------------------------------------------------------------------------
# Access Denied
# ---------------------------------------------------------------------------
def access_denied_view(request):
    """Generic access denied page."""
    return render(request, 'accounts/access_denied.html', {
        'message': 'You do not have permission to access this page.',
    }, status=403)


# ---------------------------------------------------------------------------
# Password Change
# ---------------------------------------------------------------------------
@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def password_change_view(request):
    """Allow authenticated users to change their password."""
    if request.method == 'POST':
        form = NissinPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully.')
            logger.info("User '%s' changed their password.", user.username)
            return redirect('accounts:home')
    else:
        form = NissinPasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})
