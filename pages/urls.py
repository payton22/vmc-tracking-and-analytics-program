from django.urls import path, include
#from django.contrib import admin
from .forms import CustomSetPasswordForm
from .views import *
from django.contrib.auth import views as auth_views


# manages the urls associated with the pages app
urlpatterns = [
    path('', landingPageView, name='landingPage'),
    
    path('home/', homePageView, name="homePage"),
    path('import/', importPageView, name='importPage'),
    path('visualizations/', visPageView, name='visPage'),
    path('vmcadmin/', vmcAdminPageView, name='vmcAdminPage'),
    path('vmcadmin/changePassword', changePassView, name='changePassPage'),
    path('vmcadmin/changeEmail', changeEmailView, name='changeEmailPage'),
    path('vmcadmin/changeProfileInfo', changeProfileView, name='changeProfilePage'),
    path('vmcadmin/ViewAccountsList', accountsView, name='accountsView'),
    path('vmcadmin/ViewAccountsList/newAccount', newAccount, name='newAccount'),
    path('vmcadmin/ViewAccountsList/<str:emailAddress>/', otherAccountOptions, name='otherAccountOptions'),
    path('vmcadmin/deleteAccount/<str:emailAddress>/', deleteAccount, name='deleteAccount'),
    path('password_reset/', PassReset, name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', ChangePass, name='password_reset_confirm'),
    path('password_reset_complete/', successfullyChangedPass, name='password_reset_complete'),
    path('', include('django.contrib.auth.urls')),
]

# path('password_reset', auth_views.PasswordResetView.as_view(template_name='pages/forgotPassword.html'), name='password_reset')
