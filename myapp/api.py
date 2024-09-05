import requests
from myapp import CLIENT_ID, CLIENT_SECRET
from datetime import datetime, timedelta
from myapp.models.category import Category


class TwitchAPI:
    base_url = "https://api.twitch.tv/helix/"

    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json()["access_token"]

    def _get_headers(self):
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

    def get_clips(self, category, set_id, get_from, first):
        url = self.base_url + "clips"
        params = {
            "first": first,
            "started_at": (datetime.now() - timedelta(get_from)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "ended_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        cat_id_name = "broadcaster_id" if category == Category.STREAMER else "game_id"
        params[cat_id_name] = set_id

        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()["data"]

    def _get_id(self, endpoint, name, name_key):
        url = f"{self.base_url}{endpoint}"
        params = {name_key: name}
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        data = response.json().get("data")
        if not data:
            raise ValueError(f"No data found for name: {name}")
        return data[0]["id"], data[0][name_key]

    def get_broadcaster_id(self, name: str) -> tuple[str, str]:
        return self._get_id("users", name, "login")

    def get_game_id(self, name: str) -> tuple[str, str]:
        return self._get_id("games", name, "name")
