from django.db import models

from django.conf import settings
from d_store.models import Product
# Create your models here.

class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_invoice_id = models.CharField(max_length=100, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    product_name = models.CharField(max_length=255,blank=True, null=True)
    quantity = models.IntegerField(default=1,blank=True, null=True)
    receipt_url = models.URLField(max_length=500, blank=True, null=True) 

    def __str__(self):
        return f"Invoice {self.stripe_invoice_id} - {self.total_amount} {self.currency}"

    class Meta:
        indexes = [
            models.Index(fields=['stripe_invoice_id']),
        ]
                
class InvoinceProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="product_invoice",null=True, on_delete=models.SET_NULL)
    payment_method = models.CharField(max_length=50,choices=[('Efectivo','Efectivo'),('Tarjeta','Tarjeta')])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    quantity = models.IntegerField(default=1,blank=True, null=True)
    receipt_url = models.URLField(max_length=500, blank=True, null=True) 
    
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='Invoince_added',on_delete=models.CASCADE,null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='Invoince_updated',on_delete=models.CASCADE,null=True, blank=True )
    
    
    def __str__(self):
        return f"{self.user.first_name } - {self.product.brand}"
    
    