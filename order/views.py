from django.shortcuts import render
from django.http import HttpRequest, JsonResponse

from .services.services import refresh_file, get_data


def index(request: HttpRequest):
    refresh_file()
    return render(request, 'index.html')


def get_data_view(request: HttpRequest):
    return JsonResponse(get_data())
