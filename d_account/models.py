from django.db import models
from django.contrib.auth.models import User

# Create your models here.
STATUS = (
    ('tienda','tienda'),
    ('entragado','entragado'),
    ('transito','transito'),
)


class Pedidos(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_pedidos")
    product_name = models.CharField(max_length=255,null=True, blank=True)
    date_request = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS,null=True, blank=True)
    
    checked = models.BooleanField(null=True, blank=True,default=False)
    checked_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user} - {self.product_name}"
    
    
    class Meta:
        ordering = ['date_request']
        verbose_name = "Pedidos"
        verbose_name_plural = "Pedidos"
    