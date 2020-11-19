from datetime import datetime, timedelta
from jose import JWTError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Application imports
from .configs import cfg
from .security import Security, Token, TokenData
from .api.rfm import endpoints

# Password: EIsegmentation@2020#4
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


async def is_user_authorized(token: str = Depends(oauth2_scheme)):
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

    is_authorized = sec_instance.verify_token_username(
        token_username=token_data.sys_username)

    if not is_authorized:
        raise credentials_exception

    return is_authorized


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm =
                                 Depends()):
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


app.include_router(
    endpoints.router,
    prefix="/rfm",
    tags=["rfm"],
    dependencies=[Depends(is_user_authorized)],
    responses={404: {"description": "Not found"}},
)
