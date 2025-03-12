from django.urls import path, re_path

from prices.consumer import CryptoTrackerConsumer
urlpatterns = [
    re_path(r"ws/prices/(?P<price_pair>\w+)$", CryptoTrackerConsumer.as_asgi()),
]

