class JiotvUnauthorizedException(Exception):
    def __init__(self, name: str):
        self.name = name


class JiotvSessionExpiredException(Exception):
    def __init__(self, name: str):
        self.name = name
