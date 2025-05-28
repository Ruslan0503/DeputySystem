from django.urls import path,include

from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('api/token/refresh/', views.RefreshTokenFunction.as_view(), name="toke_refresh"),
    path('addsomeonenew/', views.AddSomeoneNew.as_view(), name="addsomeonenew"),
    path('manageusers/', views.ManageUsers.as_view(), name="manageusers"),
    path('organizesession/', views.OrganizeSessions.as_view(), name="organizesession"),
    path('organizesessionapi/', views.OrganizeSessionApiVie.as_view(), name="organizesessionapi"),
    path('voting/<int:id>/', views.VotingTemplateView.as_view(), name = "voting"),
    path('checkattendance/', views.CheckAttendenceTemplate, name = "checkattendance"),
    path('logout/', views.logoutFunction, name="logout"),
    path('AddOkrug/', views.AddOkrug, name="AddOkrug"),
    #

    path('votingapiview/<int:id>/', views.VotingApiView.as_view(), name="votingapiview"),
    path('adjourmentmeeting/<int:id>', views.AdjourmentMeeting.as_view(), name="adjourmentmeeting"),


]
