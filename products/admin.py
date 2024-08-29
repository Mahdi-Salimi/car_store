from django.contrib import admin
from .models import Car

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
