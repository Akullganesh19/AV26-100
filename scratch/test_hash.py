from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "admin123"
hashed = pwd_context.hash(password)
print(f"Hashed: {hashed}")
print(f"Verified: {pwd_context.verify(password, hashed)}")
