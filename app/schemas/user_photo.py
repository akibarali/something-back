from pydantic import BaseModel, ConfigDict


class UserPhotoRead(BaseModel):
    id: int
    user_id: int
    photo_url: str

    model_config = ConfigDict(from_attributes=True)
