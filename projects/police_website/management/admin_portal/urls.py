from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login",views.login_user, name="login"),
    path("register", views.create_user_profile, name="register"),
    path("create_user", views.create_user, name="user"), 
    path("dashboard", views.dashboard, name="dashboard"),
    path("logout", views.user_logout, name="logout"),
    path("attendance", views.attendance, name="attendance"),
    path("application", views.application, name="application"),
    path("chatroom", views.chatroom, name="chatroom"),
    path("loan", views.load_application, name="loan"),
    path("role", views.user_role, name="role"),
]
