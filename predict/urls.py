from django.urls import path
from .views import index, ask_question, login_view, logout_view, signup_view

urlpatterns = [
    path('', index, name='index'),
    path('ask-question/', ask_question, name='ask_question'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
]