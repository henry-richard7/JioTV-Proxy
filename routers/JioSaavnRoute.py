from typing import Union

from fastapi import APIRouter, Request, FastAPI, Depends
from fastapi.responses import PlainTextResponse, Response

from fastapi.templating import Jinja2Templates

from Modules.JioSaavn import JioSaavnApi

from models.JioSaavn import (
    HomeModels,
    SearchModel,
    SongDetailsModel,
    AlbumDetailsModel,
    ArtistDetailsModel,
    PlaylistDetailsModel,
)

router = APIRouter(tags=["Jio Saavn"])


@router.get("/api/home")
async def api_homepage(
    language: HomeModels.Languages = HomeModels.Languages.Tamil,
    jio_saavn: JioSaavnApi = Depends(JioSaavnApi),
) -> HomeModels.HomePageResponse:
    home_page_contents = await jio_saavn.home_page(language)
    return home_page_contents


@router.get("/api/home")
async def api_homepage(
    language: HomeModels.Languages = HomeModels.Languages.Tamil,
    jio_saavn: JioSaavnApi = Depends(JioSaavnApi),
) -> HomeModels.HomePageResponse:
    home_page_contents = await jio_saavn.home_page(language)
    return home_page_contents


@router.get("/api/search")
async def api_search(
    query: str,
    search_mode: SearchModel.SearchModes = SearchModel.SearchModes.SONGS,
    jio_saavn: JioSaavnApi = Depends(JioSaavnApi),
) -> Union[
    list[SearchModel.Song],
    list[SearchModel.Album],
    list[SearchModel.Artist],
    list[SearchModel.Playlist],
]:
    search_results = await jio_saavn.search(query=query, search_mode=search_mode)
    return search_results


@router.get("/api/song_details")
async def api_song_details(
    song_id: str,
    jio_saavn: JioSaavnApi = Depends(JioSaavnApi),
) -> SongDetailsModel.SongDetail:
    song_detail = await jio_saavn.song_details(song_id=song_id)
    return song_detail


@router.get("/api/album_details")
async def api_album_details(
    album_id: str,
    jio_saavn: JioSaavnApi = Depends(JioSaavnApi),
) -> AlbumDetailsModel.AlbumDetails:
    album_detail = await jio_saavn.album_details(album_id=album_id)
    return album_detail


@router.get("/api/artist_details")
async def api_artist_details(
    artists_id: str,
    jio_saavn: JioSaavnApi = Depends(JioSaavnApi),
) -> ArtistDetailsModel.ArtistDetail:
    artist_detail = await jio_saavn.artist_details(artist_id=artists_id)
    return artist_detail


@router.get("/api/playlist_details")
async def api_playlist_details(
    playlist_id: str,
    jio_saavn: JioSaavnApi = Depends(JioSaavnApi),
) -> PlaylistDetailsModel.PlaylistDetail:
    playlist_detail = await jio_saavn.playlist_details(playlist_id=playlist_id)
    return playlist_detail
