

from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.login , name="Api_login"),

]