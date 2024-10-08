import uvicorn

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from routers import JiotvRoute, JioSaavnRoute
from models.JioTV.ExceptionModels import (
    JiotvUnauthorizedException,
    JiotvSessionExpiredException,
)

from Modules.JioTV import JioTV
import logging

from sys import platform as current_platform

logger = logging.getLogger("uvicorn")
jiotv_obj = JioTV(logger)
localip = jiotv_obj.get_local_ip()


def welcome_msg():
    print("Welcome to Jio Proxy")
    print("To Watch Live-TV:")
    print(f"\tTV Web Player: http://{localip}:8000/jiotv")
    print(f"\tPlease Login at http://{localip}:8000/jiotv/login")
    print(f"\tPlaylist m3u: http://{localip}:8000/jiotv/playlist.m3u")
    print()
    print("To Access Jio Saavn:")
    print(f"\tWeb Player: http://{localip}:8000/jio_saavn/")
    print(f"\tAPI Endpoints: http://{localip}:8000/jio_saavn/api/")
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
app.include_router(JioSaavnRoute.router, prefix="/jio_saavn")


if __name__ == "__main__":
    welcome_msg()
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(config)

    if current_platform in ("win32", "cygwin", "cli"):
        import winloop

        winloop.install()
        winloop.run(server.serve())
    else:
        import uvloop  # type: ignore For UNIX based systems

        uvloop.install()
        uvloop.run(server.serve())
