"""
URL configuration for the accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('password-change/', views.password_change_view, name='password_change'),
    path('access-denied/', views.access_denied_view, name='access_denied'),
    path('dashboard/<slug:role_slug>/', views.role_dashboard_view, name='dashboard'),
    path('workspace/<slug:role_slug>/', views.role_workspace_view, name='workspace'),
]
