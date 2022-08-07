from django.db import models


class Order(models.Model):
    """Модель заказа"""

    number = models.IntegerField('Заказ №')
    price_dollars = models.IntegerField('Стоимость $')
    date = models.DateField('Срок поставки')
    price_rub = models.IntegerField('Стоимость руб')

    def __str__(self) -> str:
        return f"{self.pk}\t{self.number}\t{self.price_dollars}\t{self.date}\t{self.price_rub}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class GoogleSheetsFile(models.Model):
    """Модель файла с google sheets для сохранения последнего файла"""

    edit_date = models.DateTimeField('Дата последнего изменения', null=True)
    file = models.FileField('Файл', upload_to='', null=True)

    class Meta:
        verbose_name = 'Файл Google Sheets'
        verbose_name_plural = 'Файлы Google Sheets'
