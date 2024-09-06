from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}. It is valid for 2 minutes.'
    email_from = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, email_from, [email])

@shared_task
def send_password_reset_email(email, token_url):
    subject = 'Password Reset Request'
    message = f'Click the link below to reset your password:\n{token_url}'
    from_email = 'web3@bama.com'
    send_mail(subject, message, from_email, [email])
