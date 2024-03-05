from cryptography.fernet import Fernet
from django.conf import settings
# Generate or retrieve the secret key securely

SECRET_KEY = b'jojuT2Us7LnImZJJbfCPtW4p_J-GIR12zJd9uUS1jhE='
# Create an instance of the Fernet cipher
cipher_suite = Fernet(SECRET_KEY)
# cipher_suite = Fernet(settings.SECRET_KEY)

def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
    return decrypted_data


# t = input('\n> ')
# encrypt_data_t = encrypt_data(t)
# print({"encrypt_data_t":type(encrypt_data_t)})
# decrypt_data_t = decrypt_data(encrypt_data_t)
# print({"decrypt_data_t":decrypt_data_t})
