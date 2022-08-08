from django.shortcuts import render
from django.http import HttpRequest, JsonResponse

from .services.services import refresh_file, get_data


def index(request: HttpRequest):
    """Главная страница"""
    refresh_file()
    return render(request, 'index.html')


def get_data_view(request: HttpRequest):
    """Получение данных из БД для наполнения главной страницы данными"""
    return JsonResponse(get_data())
