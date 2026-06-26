from pwdlib import PasswordHash # pyrefly: ignore [missing-import]
from pwdlib.hashers.argon2 import Argon2Hasher # pyrefly: ignore [missing-import]

password_hash = PasswordHash((
    Argon2Hasher(
        time_cost=2,
        memory_cost=15360,
        parallelism=1,
    ),
))

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
