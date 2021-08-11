from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .activate import activate

urlpatterns = [
  path('login/', views.LoginView.as_view(), name='login'),
	path('login/<next_url>/', views.LoginView.as_view(), name='login_next'),
	path('logout/', views.logout_view, name='logout'),
  path('signup/<str:user_role>/', views.SignUpView.as_view(), name='signup'),
  path('signup/<str:user_role>/<next_url>/', views.SignUpView.as_view(), name='signup_next'),
  path('activate/<uidb64>/<token>/', activate, name='activate_account'),
	path('student/profile/update/', views.GeneralProfileSettingsUpdateView.as_view(), name='student_profile_update'),
	path('instructor/profile/update/', views.ProfileUpdateView.as_view(), name='instructor_profile_update'),
  path('change/profile/image/', views.ProfileUpdationView.as_view(), name='change_profile_picture'),
	path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
]

# Django's built-in auth views patterns 
urlpatterns += [
  path('reset_password/', 
    auth_views.PasswordResetView.as_view(
      template_name='accounts/authentications/reset_password.html'), 
    name='reset_password'),

  path('reset_password_sent/', 
    auth_views.PasswordResetDoneView.as_view(
      template_name='accounts/authentications/password_reset_sent.html'), 
    name='password_reset_done'),

  path('reset/<uidb64>/<token>', 
    auth_views.PasswordResetConfirmView.as_view(
      template_name='accounts/authentications/password_reset_form.html'),
    name='password_reset_confirm'),

  path('reset_password_complete/', 
    auth_views.PasswordResetCompleteView.as_view(
      template_name='accounts/authentications/password_reset_done.html'),
    name='password_reset_complete')
]

