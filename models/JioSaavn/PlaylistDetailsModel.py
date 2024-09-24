from pydantic import BaseModel, Field, field_validator, ValidationInfo, computed_field
from html import unescape
from datetime import datetime


class Song(BaseModel):
    id: str
    title: str = Field(..., alias="song")
    album: str
    album_id: str = Field(..., alias="albumid")
    year: str
    artist: list = Field(..., alias="primary_artists")
    artist_id: list = Field(..., alias="primary_artists_id")
    image: str
    language: str

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150", "500x500")

        elif info.field_name == "artist" or info.field_name == "artist_id":

            if info.field_name == "artist":
                return [unescape(v) for v in value.split(", ")]
            else:
                return value.split(", ")

        elif isinstance(value, str):
            return unescape(value)

        else:
            return value


class PlaylistDetail(BaseModel):
    id: str = Field(..., alias="listid")
    title: str = Field(..., alias="listname")
    image: str
    list_count: str
    songs: list[Song]
    last_updated: int

    @computed_field
    @property
    def last_update_string(self) -> str:
        dt_object = datetime.fromtimestamp(self.last_updated)
        return dt_object.strftime("%Y-%m-%d %I:%M:%S %p")

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if isinstance(value, str):
            return unescape(value)

        else:
            return value
