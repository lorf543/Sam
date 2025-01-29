from django.contrib import admin

from .models import Invoice,InvoinceProduct

# Register your models here.


admin.site.register(Invoice)
admin.site.register(InvoinceProduct)