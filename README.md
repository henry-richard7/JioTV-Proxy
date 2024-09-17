# JioTV-Proxy

JioTV proxy developed using Python and FastAPI framework.

# Total Downloads

![Downloads](https://img.shields.io/github/downloads/henry-richard7/JioTV-Proxy/total.svg?style=for-the-badge&logo=github)

# How to use (From Binary)

- Download the latest for your platform from [Releases](https://github.com/henry-richard7/JioTV-Proxy/releases)
- Run JioTV file.
- Login to your Jio Account using OTP at http://localhost:8000/login.
- To play live channels on web http://localhost:8000.
- To play live channels in media player such as vlc http://localhost:8000/playlist.m3u
- To play live channels on your local network http://<your_local_ip>:8000/playlist.m3u (You can get this from console when running the app.)

# How To Use (Using Docker)

- Clone or Download this repo.
- In terminal `cd JioTV-Proxy`
- Next type `docker build -t jiotv-proxy .` and press enter and wait for build.
- Next type `docker run -p 8000:8000 jiotv-proxy` and press enter.

# How To Use (From Source)

- Clone or Download this repo.
- Install required dependencies `pip install -r requirements.txt`
- To run the py file, on a terminal in the root folder and type `python3 main.py` or `python main.py`
- Follow the above steps.

# Known Issues

- Sony channels will not play.

# Auto Build

This repo uses github actions to build binary for x86_64.
