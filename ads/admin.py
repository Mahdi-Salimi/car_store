from django.contrib import admin
from ads.models import Ad
from products.models import Car

class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'seller', 'is_promoted', 'start_date', 'end_date')
    list_filter = ('is_promoted', 'start_date', 'end_date')
    search_fields = ('car__title', 'seller__username')
    ordering = ('-start_date',)
    date_hierarchy = 'start_date'
    autocomplete_fields = ['car', 'seller']

admin.site.register(Ad, AdAdmin)
