from typing import Optional

from fastapi import APIRouter, Request, Depends, FastAPI
from fastapi.responses import PlainTextResponse, Response

from fastapi.templating import Jinja2Templates

from models.JioTV.ExceptionModels import (
    JiotvUnauthorizedException,
    JiotvSessionExpiredException,
)

from Modules.JioTV import JioTV
from time import time

from os import path

import sqlite3
import logging

from contextlib import asynccontextmanager
import asyncio

from scheduler.asyncio import Scheduler
from datetime import timedelta

logger = logging.getLogger("uvicorn")
jiotv_obj = JioTV(logger)
localip = jiotv_obj.get_local_ip()


def convert(m3u_file: str):
    m3u_json = []
    lines = m3u_file.split("\n")
    for line in lines:
        if line.startswith("#EXTINF"):
            channelInfo = {}
            logoStartIndex = line.index('tvg-logo="') + 10
            logoEndIndex = line.index('"', logoStartIndex)
            logoUrl = line[logoStartIndex:logoEndIndex]
            groupTitleStartIndex = line.index('group-title="') + 13
            groupTitleEndIndex = line.index('"', groupTitleStartIndex)
            groupTitle = line[groupTitleStartIndex:groupTitleEndIndex]
            titleStartIndex = line.rindex(",") + 1
            title = line[titleStartIndex:].strip()
            link = lines[lines.index(line) + 1]
            channelInfo["logo"] = logoUrl
            channelInfo["group_title"] = groupTitle
            channelInfo["title"] = title
            channelInfo["link"] = link
            m3u_json.append(channelInfo)
    result = m3u_json
    return result


def store_creds(phone_number):
    # Store the credentials along with expire time in sqlite
    expire_time = time() + 3600
    db = sqlite3.connect("creds.db")
    cursor = db.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS creds(
        phone_number TEXT,
        expire NUMERIC
    )"""
    )
    cursor.execute("""INSERT INTO creds VALUES(?,?)""", (phone_number, expire_time))
    db.commit()
    db.close()


def update_expire_time(phone_number):
    expire_time = time() + 3600

    db = sqlite3.connect("creds.db")
    cursor = db.cursor()

    cursor.execute(
        """UPDATE creds SET expire = ? WHERE phone_number = ?""",
        (
            expire_time,
            phone_number,
        ),
    )
    db.commit()
    db.close()


def get_expire():
    db = sqlite3.connect("creds.db")
    cursor = db.cursor()
    cursor.execute("""SELECT expire FROM creds""")
    expire_time = cursor.fetchone()[0]
    db.close()
    return expire_time


def get_phone_number():
    db = sqlite3.connect("creds.db")
    cursor = db.cursor()
    cursor.execute("""SELECT phone_number FROM creds""")
    phone_number = cursor.fetchone()[0]
    db.close()
    return phone_number


def clear_creds():
    db = sqlite3.connect("creds.db")
    cursor = db.cursor()
    cursor.execute("""DELETE FROM creds""")
    db.commit()
    db.close()


async def jiotv_auth_verify():
    if not path.exists(path.join("data", "jio_headers.json")):
        raise JiotvUnauthorizedException(name="--")
    else:
        pass


async def background_refresh_token():
    refreshed_token = await jiotv_obj.refresh_token()
    if refreshed_token:
        jiotv_obj.update_headers()
        logger.info("[*] Session Refreshed.")

        update_expire_time(phone_number=get_phone_number())
    else:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    await background_refresh_token()
    schedule = Scheduler()
    schedule.cyclic(timedelta(minutes=45), background_refresh_token)
    yield
    schedule.delete_jobs()


router = APIRouter(lifespan=lifespan)
templates = Jinja2Templates(directory="templates/JioTV")


@router.get("/")
async def index(
    request: Request,
    query: Optional[str] = None,
    auth_session=Depends(jiotv_auth_verify),
):
    playlist_response = await jiotv_obj.get_playlists(request.headers.get("host"))
    channels = convert(playlist_response)
    search = False

    if query != "" and query is not None:
        channels = [x for x in channels if query.lower() in x["title"].lower()]
        search = True

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "channels": channels, "search": search, "query": query},
    )


@router.get("/player")
async def player(
    request: Request,
    stream_url,
    auth_session=Depends(jiotv_auth_verify),
):
    return templates.TemplateResponse(
        "player.html", {"request": request, "stream_url": stream_url}
    )


@router.get("/get_otp")
def get_otp(phone_no):
    return jiotv_obj.sendOTP(phone_no.replace("+91", ""))


@router.get("/createToken")
def createToken(phone_number, otp):
    phone_number = phone_number.replace("+91", "")
    """
    A function that creates a token for the given phone_number and otp.

    Parameters:
        phone_number (str): The phone_number of the user.
        otp (str): The otp of the user.

    Returns:
        str: The login response containing the token.
    """
    if path.exists(path.join("creds.db")):
        logger.warning("[!] Creds already available. Clearing existing creds.")
        clear_creds()

    else:
        logger.info("[-] First Time Logging in.")

    login_response = jiotv_obj.login(phone_number, otp)
    if login_response == "[SUCCESS]":
        store_creds(phone_number)
        jiotv_obj.update_headers()
        return login_response

    return login_response


@router.get("/login")
async def loginJio(request: Request):
    """
    Get the login page.

    Parameters:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: The response containing the login page HTML template.
    """
    return templates.TemplateResponse("otp_login.html", {"request": request})


@router.get("/playlist.m3u")
async def get_playlist(
    request: Request,
    auth_session=Depends(jiotv_auth_verify),
):
    """
    Retrieves a playlist in the form of an m3u file.

    Returns:
        A PlainTextResponse object containing the playlist in the specified media type.
    """
    playlist_response = await jiotv_obj.get_playlists(request.headers.get("host"))
    return PlainTextResponse(playlist_response, media_type="application/x-mpegurl")


@router.get("/m3u8")
async def get_m3u8(
    cid,
    auth_session=Depends(jiotv_auth_verify),
):
    """
    Retrieves the m3u8 playlist for a given channel ID.

    Parameters:
    - cid: The ID of the channel to retrieve the m3u8 playlist for. (type: any)

    Returns:
    - The m3u8 playlist for the specified channel. (type: PlainTextResponse)
    """
    channel_response = await jiotv_obj.get_channel_url(cid)
    return PlainTextResponse(channel_response, media_type="application/x-mpegurl")


@router.get("/get_audio")
async def get_multi_audio(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_auth_verify),
):
    """
    A function that handles the GET request to retrieve audio.

    Parameters:
    - uri (str): The URI of the audio.
    - cid (str): The CID (Client ID) of the audio.
    - cookie (str): The cookie associated with the audio.

    Returns:
    - Response: The response object containing the audio.
    """
    audio_response = await jiotv_obj.get_audio(uri, cid, cookie)
    return Response(audio_response, media_type="application/x-mpegurl")


@router.get("/get_subs")
async def get_subtitles(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_auth_verify),
):
    """
    Retrieves subtitles for a given URI using the specified CID and cookie.

    Args:
        uri (str): The URI for which to retrieve subtitles.
        cid (str): The CID associated with the URI.
        cookie (str): The cookie required for authentication.

    Returns:
        str: The subtitles for the specified URI.

    """
    subs_response = await jiotv_obj.get_subs(uri, cid, cookie)
    return Response(subs_response)


@router.get("/get_vtt")
async def get_vtt_(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_auth_verify),
):
    resp = await jiotv_obj.get_vtt(uri, cid, cookie)
    return PlainTextResponse(resp, media_type="text/vtt")


@router.get("/get_ts")
async def get_tts(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_auth_verify),
):
    """
    A function that handles GET requests to the "/get_ts" endpoint.

    Parameters:
    - uri (str): The URI for the request.
    - cid (str): The CID for the request.
    - cookie (str): The cookie for the request.

    Returns:
    - Response: Gets the segments from the specified URI.
    """
    tts_response = await jiotv_obj.get_ts(uri, cid, cookie)
    return Response(tts_response, media_type="video/MP2T")


@router.get("/get_key")
async def get_keys(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_auth_verify),
):
    """
    Retrieves a key from the specified URI using the provided CID and cookie.

    Parameters:
    - uri (str): The URI from which to retrieve the key.
    - cid (str): The CID associated with the key.
    - cookie (str): The cookie to use for authentication.

    Returns:
    - Response: The response containing the DRM key.
    """
    key_response = await jiotv_obj.get_key(uri, cid, cookie)
    return Response(key_response, media_type="application/octet-stream")


@router.get("/play")
async def play(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_auth_verify),
):
    """
    This function is a route handler for the "/play" endpoint of the API. It expects three parameters:

    - `uri`: A string representing the URI.
    - `cid`: A string representing the CID.
    - `cookie`: A string representing the cookie.

    The function calls the `final_play` function passing in the `uri`, `cid`, and `cookie` parameters, and returns the result as a `PlainTextResponse` object with the media type set to "application/x-mpegurl".

    Returns:
    - A `PlainTextResponse` object with the media type set to "application/x-mpegurl".
    """
    final_play_response = await jiotv_obj.final_play(uri, cid, cookie)
    return PlainTextResponse(final_play_response, media_type="application/x-mpegurl")
