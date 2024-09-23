from pydantic import BaseModel, Field, field_validator, ValidationInfo
from html import unescape


class Song(BaseModel):
    id: str
    song: str
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
    list_count: str
    songs: list[Song]

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if isinstance(value, str):
            return unescape(value)

        else:
            return value
