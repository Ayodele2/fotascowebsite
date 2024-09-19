import bcrypt

# Create your tests here.
def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password_bytes)

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

print(verify_password("dare1234", "$2b$12$4XEGzwrF3xTtc8weKLz74eN6uuOO.4HpVVollvdi06TxZOyCDrbIO"))