# admin.py — Cleaned
# This file is now used only for admin password hashing utility

from werkzeug.security import generate_password_hash

def create_hashed_password(plain_password):
    return generate_password_hash(plain_password)

# Example usage:
if __name__ == '__main__':
    password = input("Enter new admin password: ")
    print("Hashed password:", create_hashed_password(password))
