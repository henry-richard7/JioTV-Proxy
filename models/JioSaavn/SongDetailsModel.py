from pydantic import BaseModel, Field, field_validator, ValidationInfo, computed_field
from html import unescape
from Modules import JioSaavn


class SongDetail(BaseModel):
    id: str
    title: str = Field(..., alias="song")
    album: str
    albumid: str
    year: str
    artist: list = Field(..., alias="primary_artists")
    artist_id: list = Field(..., alias="primary_artists_id")
    image: str
    play_count: int
    encrypted_media_url: str
    duration: str
    release_date: str

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

    @computed_field
    @property
    def decoded_stream_link(self) -> str:
        jio_saavn_api = JioSaavn.JioSaavnApi()
        return jio_saavn_api.decrypt_url(self.encrypted_media_url)
