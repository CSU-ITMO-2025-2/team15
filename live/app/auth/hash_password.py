from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashPassword:
  def create_hash(self, password: str):
    password_bytes = password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)

  def verify_hash(self, plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
