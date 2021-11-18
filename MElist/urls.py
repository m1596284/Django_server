from django.urls import path
from . import views

app_name = "MElist"
urlpatterns = [
    path('', views.MElist, name='MElist'),
]