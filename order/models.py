from django.db import models


class Order(models.Model):
    """Модель заказа"""

    number = models.IntegerField('Заказ №')
    price_dollars = models.IntegerField('Стоимость $')
    date = models.DateField('Срок поставки')
    price_rub = models.IntegerField('Стоимость руб')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class GoogleSheetsFile(models.Model):
    """Модель файла с google sheets для сохранения последнего файла"""

    edit_date = models.DateTimeField('Дата последнего изменения')
    file = models.FileField('Файл', upload_to='')
