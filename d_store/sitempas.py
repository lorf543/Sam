from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Car

class StaticSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):  # Corrección: `item()` → `items()`
        return ['home']

    def location(self, item):
        return reverse(item)

class CarSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return Car.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()  # Utiliza `get_absolute_url` del modelo
