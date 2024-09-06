import random
def generate_otp(length=6):
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    otp = "".join(random.choice(digits) for _ in range(length))
    return otp


