from datetime import timedelta

JWT_SECRET = "your-super-secret-key-change-this"
JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRE = timedelta(days=1)