from django.contrib import admin
from .models import Product, Cart, CartItem

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price']
    list_filter = ['category']
    search_fields = ['name', 'description']

admin.site.register(Cart)
admin.site.register(CartItem)
