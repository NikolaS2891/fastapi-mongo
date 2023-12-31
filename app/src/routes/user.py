from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.models.user_model import ShowUserModel

from ..config.database import Users
from ..config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from ..dependecies import authenticate_user, create_access_token, get_current_user

router = APIRouter()


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    await Users.update_one(
        {"username": form_data.username},
        {
            "$set": {
                "last_login": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
                "is_active": "true",
            }
        },
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/current_user", response_description="Current User", response_model=ShowUserModel)
async def current_user(current_user: ShowUserModel = Depends(get_current_user)):
    return current_user
