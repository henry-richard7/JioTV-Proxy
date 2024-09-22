from pydantic import BaseModel, computed_field, Field, field_validator, ValidationInfo

class Songs(BaseModel):
    id:str
    title:str = Field(...,alias='song')
    album:str
    year:str
    artist:str = Field(...,alias='music')
    artist_id:str = Field(...,alias='music_id')
    image:str

class AlbumDetails:
    title: str
    name : str
    year : str
    release_date : str
    primary_artists : list
    primary_artists_id : list
    albumid : str
    perma_url : str
    image : str
    
    @field_validator('primary_artists','primary_artists_id',mode='before')
    def string_to_list(cls, value:str,info:ValidationInfo):
        if info.field_name == "image":
            return value.replace("150x150",'500x500')
        elif isinstance(value,str):
            return value.split(", ")