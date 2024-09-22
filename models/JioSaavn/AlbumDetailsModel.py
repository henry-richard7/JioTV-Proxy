from pydantic import BaseModel, Field, field_validator, ValidationInfo
from html import unescape


class AlbumInput(BaseModel):
    album_id: str


class Song(BaseModel):
    id: str
    title: str = Field(..., alias="song")
    album: str
    albumid: str
    year: str
    artist: str = Field(..., alias="music")
    artist_id: str = Field(..., alias="music_id")
    image: str
    play_count: str
    encrypted_media_url: str
    duration: str
    release_date: str

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150", "500x500")
        else:
            return unescape(value)


class AlbumDetail(BaseModel):
    title: str
    name: str
    year: str
    release_date: str
    primary_artists: list
    primary_artists_id: list
    albumid: str
    perma_url: str
    image: str

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150", "500x500")
        elif (
            info.field_name == "primary_artists"
            or info.field_name == "primary_artists_id"
        ):
            return value.split(", ")
        else:
            return unescape(value)


class AlbumDetails(BaseModel):
    album_detail: AlbumDetail
    songs: list[Song]
