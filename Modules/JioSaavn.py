from typing import Union
from httpx import AsyncClient
import base64
from pyDes import des, ECB, PAD_PKCS5
from models.JioSaavn import HomeModels, AlbumDetailsModel, SearchModel


class JioSaavnApi:
    def __init__(self) -> None:
        self.des_cipher = des(
            b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5
        )
        self.jio_api_base_url = "https://www.jiosaavn.com/api.php"

    async def decrypt_url(self, url: str) -> str:
        enc_url = base64.b64decode(url.strip())

        dec_url = self.des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode("utf-8")
        dec_url = dec_url.replace("_96.mp4", "_320.mp3")
        return dec_url

    async def home_page(
        self, home_input: HomeModels.HomeInput
    ) -> HomeModels.HomePageResponse:
        cookies = {"L": home_input.language.value}

        request_params = {"__call": "content.getHomepageData"}
        async with AsyncClient() as async_client:
            resp = await async_client.get(
                self.jio_api_base_url, cookies=cookies, params=request_params
            )

        resp = resp.json()

        new_albums = [
            HomeModels.NewAlbumItem(**album) for album in resp.get("new_albums")
        ]
        featured_playlists = [
            HomeModels.FeaturedPlaylistItem(**featured_playlist)
            for featured_playlist in resp.get("featured_playlists")
        ]
        charts = [HomeModels.ChartItem(**chart) for chart in resp.get("charts")]

        return HomeModels.HomePageResponse(
            new_albums=new_albums, featured_playlists=featured_playlists, charts=charts
        )

    async def album_details(
        self,
        album_id: AlbumDetailsModel.AlbumInput,
    ) -> AlbumDetailsModel.AlbumDetails:

        request_params = {
            "__call": "content.getAlbumDetails",
            "albumid": album_id.album_id,
        }
        async with AsyncClient() as async_client:
            resp = await async_client.get(self.jio_api_base_url, params=request_params)

        resp = resp.json()

        album_details = AlbumDetailsModel.AlbumDetail(**resp)
        songs = [AlbumDetailsModel.Song(**song) for song in resp.get("songs")]

        result = AlbumDetailsModel.AlbumDetails(album_detail=album_details, songs=songs)
        return result

    async def search(
        self,
        search_input: SearchModel.SearchInputModel,
    ) -> Union[
        list[SearchModel.Song],
        list[SearchModel.Album],
        list[SearchModel.Artist],
        list[SearchModel.Playlist],
    ]:
        request_params = {
            "__call": search_input.search_mode.value,
            "_format": "json",
            "_marker": "0",
            "n": "151353",
            "api_version": "4",
            "ctx": "web6dot0",
            "q": search_input.query,
        }
        async with AsyncClient() as async_client:
            resp = await async_client.get(self.jio_api_base_url, params=request_params)

        resp: dict = resp.json()

        if search_input.search_mode == SearchModel.SearchModes.SONGS:
            return [SearchModel.Song(**song) for song in resp.get("results")]

        elif search_input.search_mode == SearchModel.SearchModes.ALBUMS:
            return [SearchModel.Album(**album) for album in resp.get("results")]

        elif search_input.search_mode == SearchModel.SearchModes.ARTISTS:
            return [SearchModel.Artist(**artist) for artist in resp.get("results")]

        elif search_input.search_mode == SearchModel.SearchModes.PLAYLISTS:
            return [
                SearchModel.Playlist(**playlist) for playlist in resp.get("results")
            ]

        return None
