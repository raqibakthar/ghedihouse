from django.urls import path
from . import views
from .views import *


urlpatterns = [

    path('',views.manager_dashboard,name='manager_dashboard')

] 