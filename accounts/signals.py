from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group


from accounts.models import CustomUser, BuyerUserProfile, SellerUserProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == CustomUser.UserType.BUYER:
            BuyerUserProfile.objects.create(user=instance)
            group, _ = Group.objects.get_or_create(name='buyer')
            if group not in instance.groups.all():
                instance.groups.add(group)
        elif instance.user_type == CustomUser.UserType.SELLER:
            SellerUserProfile.objects.create(user=instance)
            group, _ = Group.objects.get_or_create(name='seller')
            if group not in instance.groups.all():
                instance.groups.add(group)
