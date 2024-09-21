import uvicorn
import multiprocessing

from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import PlainTextResponse, Response, JSONResponse

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from Modules.utils import JioTV
from time import time

from os import path

import sqlite3
import logging

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


def check_session():
    """
    Check if the user is logged in and if the session has expired.

    Returns:
        - "ALL OK" if the user is logged in and the session has not expired.
        - "Expired" if the user is logged in but the session has expired.
        - "Not Logged In" if the user is not logged in.
    """

    expire_time = (
        get_expire() if path.exists(path.join("data", "jio_headers.json")) else 0
    )
    current_time = time()

    if (
        path.exists(path.join("data", "jio_headers.json"))
        and expire_time > current_time
    ):
        return "ALL OK"

    elif (
        path.exists(path.join("data", "jio_headers.json"))
        and expire_time < current_time
    ):
        logger.warning("[!] Session has expired")

        return "Expired"

    else:
        logger.warning(f"Not Logged In. Go to http://{localip}:8000/login")
        return "Not Logged In"


def welcome_msg():
    print("Welcome to JioTV-Proxy")
    print(f"Web Player: http://{localip}:8000/")
    print(f"Please Login at http://{localip}:8000/login")
    print(f"Playlist m3u: http://{localip}:8000/playlist.m3u")
    print()


class JiotvUnauthorizedException(Exception):
    def __init__(self, name: str):
        self.name = name


class JiotvSessionExpiredException(Exception):
    def __init__(self, name: str):
        self.name = name


async def jiotv_authenticated_depends():
    token_check = check_session()

    if token_check == "Not Logged In":
        raise JiotvUnauthorizedException
    elif token_check == "Expired":

        refreshed_token = await jiotv_obj.refresh_token()

        if refreshed_token:
            jiotv_obj.update_headers()
            logger.info("[*] Session Refreshed.")

            update_expire_time(phone_number=get_phone_number())
        else:
            raise JiotvSessionExpiredException
    else:
        pass


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(JiotvUnauthorizedException)
async def jiotv_unauthorized_exception_handler(
    request: Request, exc: JiotvUnauthorizedException
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "error": "Session not authenticated.",
            "details": f"Seems like you are not logged in, please login by going to http://{request.client.host}:8000/login",
        },
    )


@app.exception_handler(JiotvSessionExpiredException)
async def jiotv_session_expired_exception_handler(
    request: Request, exc: JiotvSessionExpiredException
):
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={
            "status_code": status.HTTP_410_GONE,
            "error": "Session Expired.",
            "details": f"Seems like sessions has been expired, please login again at http://{request.client.host}:8000/login",
        },
    )


@app.get("/")
async def index(
    request: Request,
    query: Optional[str] = None,
    auth_session=Depends(jiotv_authenticated_depends),
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


@app.get("/player")
async def player(
    request: Request,
    stream_url,
    auth_session=Depends(jiotv_authenticated_depends),
):
    return templates.TemplateResponse(
        "player.html", {"request": request, "stream_url": stream_url}
    )


@app.get("/get_otp")
def get_otp(phone_no):
    return jiotv_obj.sendOTP(phone_no.replace("+91", ""))


@app.get("/createToken")
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


@app.get("/login")
async def loginJio(request: Request):
    """
    Get the login page.

    Parameters:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: The response containing the login page HTML template.
    """
    return templates.TemplateResponse("otp_login.html", {"request": request})


@app.get("/playlist.m3u")
async def get_playlist(
    request: Request,
    auth_session=Depends(jiotv_authenticated_depends),
):
    """
    Retrieves a playlist in the form of an m3u file.

    Returns:
        A PlainTextResponse object containing the playlist in the specified media type.
    """
    playlist_response = await jiotv_obj.get_playlists(request.headers.get("host"))
    return PlainTextResponse(playlist_response, media_type="application/x-mpegurl")


@app.get("/m3u8")
async def get_m3u8(
    cid,
    auth_session=Depends(jiotv_authenticated_depends),
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


@app.get("/get_audio")
async def get_multi_audio(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_authenticated_depends),
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


@app.get("/get_subs")
async def get_subtitles(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_authenticated_depends),
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


@app.get("/get_vtt")
async def get_vtt_(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_authenticated_depends),
):
    resp = await jiotv_obj.get_vtt(uri, cid, cookie)
    return PlainTextResponse(resp, media_type="text/vtt")


@app.get("/get_ts")
async def get_tts(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_authenticated_depends),
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


@app.get("/get_key")
async def get_keys(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_authenticated_depends),
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


@app.get("/play")
async def play(
    uri,
    cid,
    cookie,
    auth_session=Depends(jiotv_authenticated_depends),
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


if __name__ == "__main__":
    # This is required for windows.
    multiprocessing.freeze_support()

    welcome_msg()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
