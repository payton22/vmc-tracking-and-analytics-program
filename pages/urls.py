from django.urls import path, include
#from django.contrib import admin

from .views import *
from django.contrib.auth import views as auth_views

testForms = [SelectReportType, BarGraphAxes]
choices_dict = {}
# manages the urls associated with the pages app
urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'),
    path('survey/', surveyPageView, name='surveyPage'),
    path('manualpage/', manualPageView, name='manualPage'),
    path('home/', homePageView, name="homePage"),
    path('import/', importPageView, name='importPage'),
    path('import/gpa', importGPAView, name='importGPA'),
    #path('visualizations/', visPageView, name='visPage'),
    path('vmcadmin/', accountsView, name='vmcAdminPage'),
    path('vmcadmin/changePassword/<str:emailAddress>/', changePassView, name='changePassPage'),
    path('vmcadmin/changeEmail/<str:email>', changeEmailView, name='changeEmailPage'),
    path('vmcadmin/changeProfileInfo', changeProfileView, name='changeProfilePage'),
    path('vmcadmin/ViewAccountsList', accountsView, name='accountsView'),
    path('vmcadmin/ViewAccountsList/newAccount', newAccount, name='newAccount'),
    path('vmcadmin/ViewAccountsList/<str:emailAddress>/', otherAccountOptions, name='otherAccountOptions'),
    path('vmcadmin/deleteAccount/<str:emailAddress>/', deleteAccount, name='deleteAccount'),
    path('password_reset/', PassReset, name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', ChangePass, name='password_reset_confirm'),
    path('password_reset_complete/', successfullyChangedPass, name='password_reset_complete'),
    #path('login/', auth_views.LoginView.as_view(), name='login'), No longer needed. Leaving for now for reference -Daniel
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('changeName/<str:accountName>/', changeName, name='changeName'),
    path('changeProfilePicture/<str:accountName>', profileImageView, name='changeProfilePicture'),
    path('reports/', reportsView, name='reports'),
    path('reports/Wizard/', ReportWizardBase.as_view(FORMS), name='reportsWizard'),
    path('reports/savePreset/', savePreset, name='savePreset'),
    path('reports/viewPresets', viewPresets, name='viewPresets'),
    path('reports/presetOptions/<str:name>/', individualPresetOptions, name='individualPresetOptions'),
    path('reports/presetDeleted/<str:name>', deletePreset, name='deletePreset'),
    path('reports/createReportFromPreset/<str:name>/', createReportFromPreset, name='createReportFromPreset')
    #path('', include('django.contrib.auth.urls')),
]

# path('password_reset', auth_views.PasswordResetView.as_view(template_name='pages/forgotPassword.html'), name='password_reset')
