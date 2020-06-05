from spotipy.oauth2 import SpotifyOAuth
from json import dump, load
from definitions import CACHE_DIR
from os import environ

scopes = [
    "streaming user-library-read",
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-library-modify",
    "user-follow-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-follow-read"
]


class Config:
    def __init__(self):
        self._username = ""
        self._client_id = ""
        self._client_secret = ""
        self._redirect_uri = ""

        self._scope = " ".join(scopes)
        self.config_path = f"{CACHE_DIR}config.json"

        self.open_env()
        if not self.is_valid():
            self.open_json()

    def open_env(self):
        if all(p in environ for p in
               ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET", "SPOTIPY_REDIRECT_URI", "USERNAME"]):
            self._username = environ["USERNAME"]
            self._client_id = environ["SPOTIPY_CLIENT_ID"]
            self._client_secret = environ["SPOTIPY_CLIENT_SECRET"]
            self._redirect_uri = environ["SPOTIPY_REDIRECT_URI"]
        else:
            print("Environment variables not found")

    def open_json(self):
        """ Opens JSON with specific val that's passed to the property decorated methods """
        try:
            with open(self.config_path) as file:
                params = load(file)
                if all(p in params for p in ["username", "client_id", "client_secret", "redirect_uri"]):
                    self._username = params["username"]
                    self._client_id = params["client_id"]
                    self._client_secret = params["client_secret"]
                    self._redirect_uri = params["redirect_uri"]

        except FileNotFoundError:
            print("config.json does not exist.")

    def save_json(self):
        """ Method creates config.json in the correct dir"""
        data = {
            "username": self._username,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "redirect_uri": self._redirect_uri
        }

        with open(self.config_path, "w") as file:
            dump(data, file)
            print("Config updated")

    def get_oauth(self):
        return SpotifyOAuth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            username=self._username,
            redirect_uri=self._redirect_uri,
            scope=self._scope
        )

    def is_valid(self):
        # TODO needs work
        if len(self.client_id) != 32:
            return False
        if len(self._client_secret) != 32:
            return False
        if len(self._redirect_uri) != 0:
            return False

        return True

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, val):
        self._username = val
        self.save_json()

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, val):
        self._client_id = val
        self.save_json()

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, val):
        self._client_secret = val
        self.save_json()

    @property
    def redirect_uri(self):
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, val):
        self._redirect_uri = val
        self.save_json()
