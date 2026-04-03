# key_generator.py
from cryptography.fernet import Fernet

def generate():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("Schlüssel 'secret.key' wurde erstellt.")

if __name__ == "__main__":
    generate()