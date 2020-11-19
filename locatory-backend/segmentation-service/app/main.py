from datetime import datetime, timedelta
from jose import JWTError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Application imports
from configs import cfg
from security import Security, Token, TokenData

# Password: EIsegmentation@2020#4
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    sec_instance = Security.get_instance()

    try:
        sys_username = sec_instance.decode_token(token)
        if sys_username is None:
            raise credentials_exception
        token_data = TokenData(sys_username=sys_username)
    except JWTError:
        raise credentials_exception

    user = sec_instance.verify_token_username(
        token_username=token_data.sys_username)

    if user is None:
        raise credentials_exception

    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """ Endpoint to get access token
    """
    sec_instance = Security.get_instance()

    sys_username = sec_instance.authenticate_user(
        form_data.username, form_data.password)

    if not sys_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = sec_instance.create_access_token(
        data={"sub": sys_username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get('/')
async def index(current_user: str = Depends(get_current_user)):
    return {"Real": "Python"}
