from pydantic import BaseModel, computed_field, Field, field_validator, ValidationInfo
from enum import Enum
from html import unescape


class Languages(Enum):
    Tamil = "tamil"
    Hindi = "hindi"
    English = "english"
    Telugu = "telugu"
    Punjabi = "punjabi"
    Marathi = "marathi"
    Gujarati = "gujarati"
    Bengali = "bengali"
    Kannada = "kannada"
    Bhojpuri = "bhojpuri"
    Malayalam = "malayalam"
    Urdu = "urdu"
    Haryanvi = "haryanvi"
    Rajasthani = "rajasthani"
    Odia = "odia"
    Assamese = "assamese"


class HomeInput(BaseModel):
    language: Languages


class Music(BaseModel):
    id: str
    name: str

    @field_validator("*", mode="before")
    def html_unescape(cls, value: str, info: ValidationInfo):
        if isinstance(value, str):
            return unescape(value)

        else:
            return value


class Songs(BaseModel):
    name: str
    image: str

    @field_validator("*", mode="before")
    def html_unescape(cls, value: str, info: ValidationInfo):
        if isinstance(value, str):
            return unescape(value)

        else:
            return value


class ChartItem(BaseModel):
    listid: str
    listname: str
    image: str
    weight: int
    songs: list[Songs]
    perma_url: str

    @field_validator("*", mode="before")
    def html_unescape(cls, value: str, info: ValidationInfo):
        if isinstance(value, str):
            return unescape(value)

        else:
            return value


class NewAlbumItem(BaseModel):
    query: str
    text: str
    year: str
    image: str
    albumid: str
    title: str
    Artist: dict = Field(..., alias="Artist", exclude=True)
    weight: int
    language: str

    @computed_field
    @property
    def artists(self) -> list[Music]:
        return [Music(**artist) for artist in self.Artist.get("music")]

    @field_validator("*", mode="before")
    def html_unescape(cls, value: str, info: ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150", "500x500")

        elif isinstance(value, str):
            return unescape(value)

        else:
            return value


class FeaturedPlaylistItem(BaseModel):
    listid: str
    secondary_subtitle: str
    firstname: str
    listname: str
    data_type: str
    count: int
    image: str
    sponsored: bool
    perma_url: str
    follower_count: str
    uid: str
    last_updated: int

    @field_validator("*", mode="before")
    def html_unescape(cls, value: str, info: ValidationInfo):
        if isinstance(value, str):
            return unescape(value)

        else:
            return value


class HomePageResponse(BaseModel):
    new_albums: list[NewAlbumItem]
    featured_playlists: list[FeaturedPlaylistItem]
    charts: list[ChartItem]
