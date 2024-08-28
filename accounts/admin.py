from django.contrib import admin
from accounts.models import CustomUser, SellerUserProfile, BuyerUserProfile

admin.site.register(CustomUser)
admin.site.register(SellerUserProfile)
admin.site.register(BuyerUserProfile)
