from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ValidationInfo,
)
from enum import Enum
from html import unescape


class SearchModes(str, Enum):
    SONGS = "search.getResults"
    ARTISTS = "search.getArtistResults"
    ALBUMS = "search.getAlbumResults"
    PLAYLISTS = "search.getPlaylistResults"


class SearchInputModel(BaseModel):
    search_mode: SearchModes
    query: str


class MoreInfo(BaseModel):
    album: str
    album_id: str
    artist: str = Field(..., alias="music")
    encrypted_media_url: str
    duration: str


class Song(BaseModel):
    id: str
    title: str
    image: str
    language: str
    year: str
    play_count: str
    more_info: MoreInfo

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150", "500x500")
        else:
            return unescape(value)


class Album(BaseModel):
    id: str
    title: str
    artist: str = Field(..., alias="subtitle")
    image: str
    language: str
    year: str

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150", "500x500")
        else:
            return unescape(value)


class Artist(BaseModel):
    name: str
    id: str
    image: str

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("50x50", "500x500")
        else:
            return unescape(value)


class Playlist(BaseModel):
    id: str
    title: str
    image: str

    @field_validator("*", mode="before")
    def image_resolution_fix(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150", "500x500")
        else:
            return unescape(value)
