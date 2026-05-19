import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserPhoto
from app.repositories.user import UserRepository
from app.repositories.user_photo import UserPhotoRepository

MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

UPLOAD_DIR = Path("media/user_photos")


class UserPhotoService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.photo_repo = UserPhotoRepository(db)

    async def _save_file(self, file: UploadFile) -> str:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, PNG, WEBP and GIF files are allowed.",
            )

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must not exceed 10 MB.",
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        ext = ALLOWED_CONTENT_TYPES[file.content_type]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as f:
            f.write(content)

        return f"/media/user_photos/{filename}"

    def _delete_file(self, photo_url: str) -> None:
        file_path = photo_url.lstrip("/")

        if os.path.exists(file_path):
            os.remove(file_path)

    async def create(self, user_id: int, file: UploadFile) -> UserPhoto | None:
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            return None

        photo_url = await self._save_file(file)

        return await self.photo_repo.create(
            user_id=user_id,
            photo_url=photo_url,
        )

    async def get_by_id(self, photo_id: int) -> UserPhoto | None:
        return await self.photo_repo.get_by_id(photo_id)

    async def get_by_user_id(self, user_id: int) -> list[UserPhoto] | None:
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            return None

        return await self.photo_repo.get_by_user_id(user_id)

    async def update(self, photo_id: int, file: UploadFile) -> UserPhoto | None:
        photo = await self.photo_repo.get_by_id(photo_id)

        if not photo:
            return None

        old_photo_url = photo.photo_url
        new_photo_url = await self._save_file(file)

        updated_photo = await self.photo_repo.update(
            photo=photo,
            photo_url=new_photo_url,
        )

        self._delete_file(old_photo_url)

        return updated_photo

    async def delete(self, photo_id: int) -> bool:
        photo = await self.photo_repo.get_by_id(photo_id)

        if not photo:
            return False

        photo_url = photo.photo_url

        await self.photo_repo.delete(photo)
        self._delete_file(photo_url)

        return True
