from datetime import datetime, timedelta
from typing import List, Union


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.models.user_model import ShowUserModel, UpdateUserModel, UserModel, UserRole

from ..config.database import Users
from ..dependecies import get_current_user, get_password_hash

router = APIRouter()


@router.get("/list_users", response_description="List all users", response_model=List[ShowUserModel])
async def list_users(current_user: UserModel = Depends(get_current_user)):
    users = await Users.find().to_list(1000)
    for user in users:
        user["is_active"] = "false"
        try:
            last_login = datetime.strptime(user["last_login"], "%m/%d/%y %H:%M:%S")
            my_delta = datetime.now() - last_login
            if my_delta <= timedelta(days=30):
                user["is_active"] = "true"
        except ValueError:
            pass

    return users


@router.get("/filter_users", response_description="Filter users", response_model=List[ShowUserModel])
async def filter_users(
    current_user: UserModel = Depends(get_current_user),
    id: Union[str, None] = None,
    username: Union[str, None] = None,
    first_name: Union[str, None] = None,
    last_name: Union[str, None] = None,
    role: Union[str, None] = None,
):
    query_params = {
        "_id": id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "role": role,
    }

    if current_user["role"] == UserRole.admin:
        users = await Users.find({key: value for key, value in query_params.items() if value is not None}).to_list(1000)
        if users:
            return users
        else:
            raise HTTPException(status_code=404, detail="There are no users for the given criteria")
    else:
        raise HTTPException(status_code=403, detail="Not having sufficient rights to modify the content")


@router.post("/create_user", response_description="Add new user", response_model=UserModel)
async def create_user(user: UserModel):
    datetime_now = datetime.now()
    user.created_at = datetime_now.strftime("%m/%d/%y %H:%M:%S")
    user.password = get_password_hash(user.password)
    user = jsonable_encoder(user)
    new_user = await Users.insert_one(user)
    await Users.update_one({"_id": new_user.inserted_id}, {"$rename": {"password": "hashed_pass"}})

    created_user = await Users.find_one({"_id": new_user.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)


@router.put(
    "/update_user/{user_id}",
    response_description="Update a user",
    response_model=UpdateUserModel,
)
async def update_user(user_id: str, user: UpdateUserModel, current_user: UserModel = Depends(get_current_user)):
    if current_user["role"] == UserRole.admin:
        user = {k: v for k, v in user.dict().items() if v is not None}

        if len(user) >= 1:
            update_result = await Users.update_one({"_id": user_id}, {"$set": user})

            if update_result.modified_count == 1:
                if (updated_user := await Users.find_one({"_id": user_id})) is not None:
                    return updated_user

        if (existing_user := await Users.find_one({"_id": user_id})) is not None:
            return existing_user

        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    else:
        raise HTTPException(status_code=403, detail="Not having sufficient rights to modify the content")


@router.delete("/delete_user/{user_id}", response_description="Delete a user")
async def delete_user(user_id: str, current_user: UserModel = Depends(get_current_user)):
    if current_user["role"] == UserRole.admin:
        delete_result = await Users.delete_one({"_id": user_id})

        if delete_result.deleted_count == 1:
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    else:
        raise HTTPException(status_code=403, detail="Not having sufficient rights to modify the content")
