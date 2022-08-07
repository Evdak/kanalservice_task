from django.contrib import admin
from django.urls import path, include

from order.urls import urlpatterns as order_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(order_urlpatterns))
]
