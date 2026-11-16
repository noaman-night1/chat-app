from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_index, name='chat_index'),
    path('api/register/', views.register_view, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/user/', views.current_user_view, name='current_user'),
    path('api/users/', views.users_list_view, name='users_list'),

]