from django.contrib import admin

from products.models import Car, CarImage, Wishlist

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'year', 'price', 'created_at')

    def get_queryset(self, request):
        return super().get_queryset(request).using('cars_database')

    def save_model(self, request, obj, form, change):
        obj.save(using='cars_database')

    def delete_model(self, request, obj):
        obj.delete(using='cars_database')

    def save_related(self, request, form, formsets, change):
        form.save_m2m()
        for formset in formsets:
            self.save_formset(request, form, formset, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save(using='cars_database')
        formset.save_m2m()

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'added_at')
    search_fields = ('user__username', 'car__title')
    list_filter = ('added_at',)
    date_hierarchy = 'added_at'
    ordering = ('-added_at',)

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'image_url')
    search_fields = ('car__title',)
    ordering = ('car',)