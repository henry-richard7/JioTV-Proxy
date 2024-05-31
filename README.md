# JioTV-Proxy

JioTV proxy developed using Python and FastAPI framework.

# New Changes

- For Sony Liv channels I have added direct stream links instead of JIO-TV stream. [Found It From Here.](https://github.com/dhruv-2015/JIOTVServer/blob/main/utils/genPlaylist.mjs)

- (2024-05-31) Added OTP login.

# How to use (From Binary)

- Download the latest for your platform from [Releases](https://github.com/henry-richard7/JioTV-Proxy/releases)
- Run JioTV file.
- Login to your Jio Account using Email at http://localhost:8000/?mode=unpw.
- Login to your Jio Account using OTP at http://localhost:8000/?mode=otp.
- To play live channels on web http://localhost:8000.
- To play live channels in media player such as vlc http://localhost:8000/playlist.m3u
- To play live channels on your local network http://<your_local_ip>:8000/playlist.m3u (You can get this from console when running the app.)

# How To Use (From Source)

- Clone or Download this repo.
- Install required dependencies `pip install -r requirements.txt`
- To run the py file, on a terminal in the root folder and type `python3 main.py` or `python main.py`
- Follow the above steps.

# Known Issues

- CN HD+ Tamil: It is noted that Cartoon Network HD+ Tamil channel does not work under API v2.0 but working in v2.1. Using v2.1 breaks other channels. Need to find a way to use v2.1 endpoint if currently playing channel is CN HD+ Tamil.
- Sony channels are not playing in Web Browser. This is due to **CORS**. To workaround Need to install [Cors Bypass Extension](https://chromewebstore.google.com/detail/cors-unblock/lfhmikememgdcahcdlaciloancbhjino?pli=1)

# Auto Build

This repo uses github actions to build binary for x86_64.
