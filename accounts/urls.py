from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'accounts'   # 👈 THIS IS REQUIRED

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="registration/password_reset_email.html",
            success_url="/accounts/password-reset/done/",
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('edit-dealer-profile/', views.edit_dealer_profile, name='edit_dealer_profile'),
   # path('request-verification/', views.request_verification, name='request_verification'),
    path('seller/verification/', views.seller_verification, name='seller_verification'),
   # path('request-verification/', views.request_verification, name='request_verification'),

]
