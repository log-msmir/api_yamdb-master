from django.utils.crypto import get_random_string


def generate_confirmation_code(length=10):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)ABCDEFGHIJKLMNPQRSTUVWXYZ'
    confirmation_code = get_random_string(length, chars)
    
    return confirmation_code
