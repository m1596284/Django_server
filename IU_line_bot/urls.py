from django.urls import path
from . import views

app_name = "IU_line_bot"
urlpatterns = [
    path('', views.line_bot_receive, name='IU_line_bot'),
]