from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ValidationInfo,
)

from models.JioSaavn.SearchModel import Song, Album
from html import unescape


class TopSongs(BaseModel):
    songs: list[Song]


class TopAlbums(BaseModel):
    albums: list[Album]


class ArtistDetail(BaseModel):
    artist_id: str = Field(..., alias="artistId")
    title: str = Field(..., alias="name")
    image: str
    listeners: str = Field(..., alias="subtitle")
    follower_count: str
    top_songs: TopSongs = Field(..., alias="topSongs")
    top_albums: TopAlbums = Field(..., alias="topAlbums")

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150", "500x500")

        elif info.field_name == "listeners":
            return value.split(" ")[-2]

        elif isinstance(value, str):
            return unescape(value)

        else:
            return value
