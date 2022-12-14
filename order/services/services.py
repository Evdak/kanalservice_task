from datetime import datetime
from django.core.files.base import ContentFile, File

from ..models import GoogleSheetsFile, Order
from kanalservice_task.settings import DOLLAR_EXCHANGE_RATE_URL
from .google_api import get_last_edit_date, get_file_data

from bs4 import BeautifulSoup
import requests

import json
import pytz
import difflib

utc = pytz.UTC


def get_data() -> dict:
    """Получение данных о заказах из БД"""
    orders = Order.objects.all().order_by('pk')
    values = {}
    all_table = []
    for el in orders:
        date = str(el.date)
        if values.get(date):
            values[date] += el.price_rub
        else:
            values[date] = el.price_rub

        all_table.append([
            el.pk,
            el.number,
            el.price_dollars,
            date,
            el.price_rub,
        ])

    return {
        'dates': list(values.keys()),  # все даты
        'values': values,  # массив JSON объектов типа: {"дата": сумма}
        'all_table': all_table,  # массив всех объектов для таблицы
        'total': sum(values.values())  # общая сумма в руб
    }


def refresh_file() -> None:
    """Обновляем данные, проверяя файла Google Sheets"""
    file, _ = GoogleSheetsFile.objects.get_or_create(
        pk=1,
        defaults={
            "file": None,
            "edit_date": None
        }
    )

    if _check_if_file_edited(file):
        _refresh_file(file)

    file.refresh_from_db()


def _refresh_file(file: GoogleSheetsFile) -> None:
    """Обновляем данные в БД,  проверяя файла Google Sheets"""
    old_values = []

    if file.file:
        try:
            with file.file.open() as f:
                old_values = json.loads(f.read())
        except FileNotFoundError:
            old_values = []

    new_values = get_file_data()['values']

    file.file = ContentFile(
        json.dumps(new_values), f"data.json")

    _refresh_db(old_values, new_values)

    file.edit_date = get_last_edit_date()
    file.save()


def _refresh_db(old_values: list, new_values: list) -> None:
    """Обновляем данные в БД"""
    old_values = _list_to_normal(old_values)
    new_values = _list_to_normal(new_values)
    dollar_exchange_rate = _get_today_dollar_exchange_rate()

    # находим различия старого и нового списка
    diff = difflib.unified_diff(old_values, new_values)

    # и удаляем или добавляем данных в БД в соответствии с различием списков
    diff_add = [el for el in diff if el.startswith('+') and ' ;; ' in el]
    diff_delete = [el for el in diff if el.startswith('-') and ' ;; ' in el]

    for el in diff_delete:
        el = el[1:].split(' ;; ')
        try:
            order = Order.objects.get(pk=int(el[0])).delete()
        except Order.DoesNotExist:
            pass

    for el in diff_add:
        el = el[1:].split(' ;; ')
        _pk, _number, _price_dollars, _date = el
        _date = datetime.strptime(_date, '%d.%m.%Y').date()
        Order.objects.get_or_create(
            pk=_pk,
            number=int(_number),
            price_dollars=int(_price_dollars),
            date=_date,
            price_rub=int(_price_dollars) * dollar_exchange_rate
        )


def _list_to_normal(ls: list):
    """Функция для форматирования списка"""
    if ls:
        for i in range(len(ls)):
            ls[i] = " ;; ".join(ls[i])
        ls.pop(0)
    return ls


def _check_if_file_edited(file: GoogleSheetsFile) -> bool:
    """Функция для проверки изменен ли Google Sheets файл"""
    return not file.edit_date or file.edit_date <= utc.localize(get_last_edit_date())


def _get_today_dollar_exchange_rate() -> float:
    """Функция для получения текущего курса доллара"""
    today = datetime.now().date()
    url = DOLLAR_EXCHANGE_RATE_URL + f"{today:%d/%m/%Y}"
    r = requests.get(url).content
    soup = BeautifulSoup(r, 'xml')

    return float(
        soup.find('Valute', {"ID": "R01235"}).find('Value').text.replace(',', '.'))
