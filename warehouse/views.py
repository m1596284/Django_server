from django.shortcuts import render
from django.http import HttpResponse
import os

# Create your views here.

def tiktok(request,video_id):
    upload_file_path = f"media/tiktok/{str(video_id)}.mp4"
    print(upload_file_path)
    if os.path.exists(upload_file_path):
        with open(upload_file_path, 'rb') as file:
            response = HttpResponse(file.read(), charset='utf-8' )
            response['Content-Type'] = f"application/mp4"
            response['Content-Disposition'] = f"inline; filename={os.path.basename(upload_file_path.encode('utf-8').decode('ISO-8859-1'))}"
            return response
