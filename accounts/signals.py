from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUser, BuyerUserProfile, SellerUserProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == CustomUser.UserType.BUYER:
            BuyerUserProfile.objects.create(user=instance)
        elif instance.user_type == CustomUser.UserType.SELLER:
            SellerUserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == CustomUser.UserType.BUYER:
        instance.buyeruserprofile.save()
    elif instance.user_type == CustomUser.UserType.SELLER:
        instance.selleruserprofile.save()
