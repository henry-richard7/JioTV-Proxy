import uvicorn
import multiprocessing

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from routers import JiotvRoute
from models.JioTV.ExceptionModels import (
    JiotvUnauthorizedException,
    JiotvSessionExpiredException,
)

from Modules.JioTV import JioTV
import logging

logger = logging.getLogger("uvicorn")
jiotv_obj = JioTV(logger)
localip = jiotv_obj.get_local_ip()


def welcome_msg():
    print("Welcome to JioTV-Proxy")
    print(f"TV Web Player: http://{localip}:8000/jiotv")
    print(f"Please Login at http://{localip}:8000/jiotv/login")
    print(f"Playlist m3u: http://{localip}:8000/jiotv/playlist.m3u")
    print()


app = FastAPI()
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
            "details": f"Seems like you are not logged in, please login by going to http://{request.client.host}:8000/jiotv/login",
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
            "details": f"Seems like sessions has been expired, please login again at http://{request.client.host}:8000/jiotv/login",
        },
    )


app.include_router(JiotvRoute.router, prefix="/jiotv")

if __name__ == "__main__":
    # This is required for windows.
    multiprocessing.freeze_support()

    welcome_msg()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
