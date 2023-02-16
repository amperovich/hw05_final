from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy

from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

passwords = [
    path(
        'change/',
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy('users:password:change_done'),
            template_name='users/password/change/form.html',
        ),
        name='change',
    ),
    path(
        'change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/password/change/done.html',
        ),
        name='change_done',
    ),
    path(
        'reset/',
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy('users:password:reset_done'),
            email_template_name='users/password/reset/email.html',
            template_name='users/password/reset/form.html',
        ),
        name='reset',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password/reset/done.html',
        ),
        name='reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password/reset/confirm.html',
            success_url=reverse_lazy('users:password:reset_complete'),
        ),
        name='reset_confirm',
    ),
    path(
        'reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password/reset/complete.html',
        ),
        name='reset_complete',
    ),
]

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path('password/', include((passwords, 'users'), namespace='password')),
]
