from django.shortcuts import render
from django.http import HttpResponse

def MElist(request):
    context = {
        'form': "form"
    }
    return render(request, 'MElist/main.html', context)