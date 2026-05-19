from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user_photo import UserPhotoRead
from app.services.user_photo import UserPhotoService

router = APIRouter(prefix="/user-photos", tags=["user photos"])


@router.post(
    "/",
    response_model=UserPhotoRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_photo(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    service = UserPhotoService(db)
    photo = await service.create(user_id=user_id, file=file)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )

    return photo


@router.get("/{photo_id}", response_model=UserPhotoRead)
async def get_user_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = UserPhotoService(db)
    photo = await service.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id={photo_id} not found.",
        )

    return photo


@router.get("/user/{user_id}", response_model=list[UserPhotoRead])
async def get_user_photos(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = UserPhotoService(db)
    photos = await service.get_by_user_id(user_id)

    if photos is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )

    return photos


@router.put("/{photo_id}", response_model=UserPhotoRead)
async def update_user_photo(
    photo_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    service = UserPhotoService(db)
    photo = await service.update(photo_id=photo_id, file=file)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id={photo_id} not found.",
        )

    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = UserPhotoService(db)
    deleted = await service.delete(photo_id=photo_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id={photo_id} not found.",
        )
