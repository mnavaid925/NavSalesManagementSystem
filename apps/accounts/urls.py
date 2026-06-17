from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

app_name = "accounts"

urlpatterns = [
    # --- auth ---
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("invite/<str:token>/", views.invite_accept_view, name="invite_accept"),

    # --- forgot / reset password (Django built-ins + custom templates) ---
    path("password/forgot/", auth_views.PasswordResetView.as_view(
        template_name="auth/password_reset.html",
        email_template_name="auth/password_reset_email.txt",
        subject_template_name="auth/password_reset_subject.txt",
        form_class=StyledPasswordResetForm,
        success_url=reverse_lazy("accounts:password_reset_done"),
    ), name="password_reset"),
    path("password/forgot/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="auth/password_reset_done.html",
    ), name="password_reset_done"),
    path("password/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="auth/password_reset_confirm.html",
        form_class=StyledSetPasswordForm,
        success_url=reverse_lazy("accounts:password_reset_complete"),
    ), name="password_reset_confirm"),
    path("password/reset/complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name="auth/password_reset_complete.html",
    ), name="password_reset_complete"),

    # --- users ---
    path("users/", views.user_list, name="user_list"),
    path("users/add/", views.user_create, name="user_create"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),

    # --- invites ---
    path("invites/", views.invite_list, name="invite_list"),
    path("invites/new/", views.invite_create, name="invite_create"),
    path("invites/<int:pk>/resend/", views.invite_resend, name="invite_resend"),
    path("invites/<int:pk>/revoke/", views.invite_revoke, name="invite_revoke"),

    # --- roles ---
    path("roles/", views.role_list, name="role_list"),
    path("roles/add/", views.role_create, name="role_create"),
    path("roles/<int:pk>/", views.role_detail, name="role_detail"),
    path("roles/<int:pk>/edit/", views.role_edit, name="role_edit"),
    path("roles/<int:pk>/delete/", views.role_delete, name="role_delete"),

    # --- profile ---
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/password/", views.change_password, name="change_password"),
]
