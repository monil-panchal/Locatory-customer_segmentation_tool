from .configs import cfg
from typing import Optional
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


class Security:
    ALGORITHM = "HS256"
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    __instance__ = None

    def __init__(self):
        """ Constructor.
        """
        if Security.__instance__ is None:
            Security.__instance__ = self
        else:
            raise Exception("You cannot create another SingletonGovt class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not Security.__instance__:
            Security()
        return Security.__instance__

    def get_system_username(self):
        return cfg.USERNAME

    def get_system_hashed_password(self):
        return cfg.PASSWORD

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str):
        sys_username = self.get_system_username()
        sys_password = self.get_system_hashed_password()

        if not sys_username or not sys_password:
            return False

        if not self.verify_password(password, sys_password):
            return False

        return sys_username

    def verify_token_username(self, token_username):
        if token_username == self.get_system_username():
            return True

        return False

    def create_access_token(self, data: dict, expires_delta: timedelta = 60):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, cfg.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_jwt

    def decode_token(self, token):
        payload = jwt.decode(token, cfg.SECRET_KEY,
                             algorithms=[self.ALGORITHM])
        sys_username: str = payload.get("sub")
        return sys_username


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sys_username: Optional[str] = None
