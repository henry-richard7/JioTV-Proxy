from httpx import AsyncClient
import base64
from pyDes import des, ECB,PAD_PKCS5
from models.JioSaavn import HomeModels

class JioSaavnApi:
    def __init__(self) -> None:
        self.des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
        self.jio_api_base_url = "https://www.jiosaavn.com/api.php"
        
    async def decrypt_url(self, url:str)->str:
        enc_url = base64.b64decode(url.strip())

        dec_url = self.des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode("utf-8")
        dec_url = dec_url.replace("_96.mp4", "_320.mp3")
        return dec_url
    
    async def home_page(self,language:str) -> HomeModels.HomePageResponse:
        cookies = {
            "L":language
        }
        
        request_params = {
            "__call":"content.getHomepageData"
        }
        async with AsyncClient() as async_client:
            resp = await async_client.get(self.jio_api_base_url,cookies=cookies,params=request_params)
            
        resp = resp.json()
        
        new_albums = [HomeModels.NewAlbumItem(**album) for album in resp.get("new_albums")]
        featured_playlists = [HomeModels.FeaturedPlaylistItem(**featured_playlist) for featured_playlist in resp.get("featured_playlists")]
        charts = [HomeModels.ChartItem(**chart) for chart in resp.get("charts")]
        
        return HomeModels.HomePageResponse(
            new_albums=new_albums,
            featured_playlists=featured_playlists,
            charts=charts
        )
        
    async def album_details(self, album_id:str):
        pass