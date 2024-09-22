from pydantic import BaseModel, computed_field, Field

class Music(BaseModel):
    id:str
    name:str
    
class Songs(BaseModel):
    name:str
    image:str
    
class ChartItem(BaseModel):
    listid:str
    listname:str
    image:str
    weight:int
    songs: list[Songs]
    perma_url:str

class NewAlbumItem(BaseModel):
    query:str
    text:str
    year:str
    image:str
    albumid:str
    title:str
    Artist:dict = Field(...,alias='Artist',exclude=True)
    weight:int
    language:str
    
    @computed_field
    @property
    def artists(self) -> list[Music]:
        return [Music(**artist) for artist in self.Artist.get('music')]
    
class FeaturedPlaylistItem(BaseModel):
    listid:str
    secondary_subtitle:str
    firstname:str
    listname:str
    data_type:str
    count:int
    image:str
    sponsored:bool
    perma_url:str
    follower_count:str
    uid:str
    last_updated:int
    
class HomePageResponse(BaseModel):
    new_albums:list[NewAlbumItem]
    featured_playlists:list[FeaturedPlaylistItem]
    charts:list[ChartItem]