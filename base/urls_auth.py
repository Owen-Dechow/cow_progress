from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login", LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout", LogoutView.as_view(template_name="auth/form.html"), name="logout"),
    path("register", views.register, name="register"),
    path("delete-account", views.delete_account, name="delete-account"),
    path("account-deleted", views.account_deleted, name="account-deleted"),
    # Password Paths
    path(
        "password-change",
        auth_views.PasswordChangeView.as_view(
            template_name="auth/password_change.html",
        ),
        name="password-change",
    ),
    path(
        "password-change/done",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="auth/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "password-reset",
        auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset.html",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/done",
        auth_views.PasswordResetDoneView.as_view(
            template_name="auth/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/complete",
        auth_views.PasswordResetDoneView.as_view(
            template_name="auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
