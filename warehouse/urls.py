from django.urls import path
from . import views

app_name = "warehouse"
urlpatterns = [
    path('tiktok/<int:video_id>', views.tiktok, name='tiktok'),
]