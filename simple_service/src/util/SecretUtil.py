import keyring
from cryptography.fernet import Fernet

class SecretUtil:
    def __init__(self, service_name):
        c = keyring.get_credential(service_name, "key" )
        key = c.password.encode() if c else None

        if key is None:
            key = Fernet.generate_key()
            keyring.set_password(service_name, "key", key.decode())

        self._fernet = Fernet(key)

    def encrypt(self, d: bytes):
        return self._fernet.encrypt(d)

    def decrypt(self, d: bytes):
        return self._fernet.decrypt(d)
