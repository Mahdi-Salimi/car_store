from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import CustomUser, SellerUserProfile, BuyerUserProfile



class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'user_type', 'phone_number', 'date_of_birth', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('user_type', 'phone_number', 'date_of_birth', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type', 'phone_number', 'date_of_birth', 'address', 'is_active', 'is_staff', 'is_superuser')}
         ),
    )

    readonly_fields = ('date_joined', 'last_login')
    search_fields = ('email', 'user_type')
    ordering = ('email',)

    filter_horizontal = ('groups', 'user_permissions',)


class BuyerUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_type',)
    search_fields = ('user__email',)
    list_filter = ('user__user_type',)

    readonly_fields = ('user',)

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'

    def user_type(self, obj):
        return obj.user.user_type

    user_type.short_description = 'User Type'


class SellerUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'company_name', 'website', 'rating', 'total_sales', 'user_type',)
    search_fields = ('user__email', 'company_name',)
    list_filter = ('user__user_type', 'rating',)

    readonly_fields = ('user', 'total_sales')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'

    def user_type(self, obj):
        return obj.user.user_type

    user_type.short_description = 'User Type'




admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BuyerUserProfile, BuyerUserProfileAdmin)
admin.site.register(SellerUserProfile, SellerUserProfileAdmin)

