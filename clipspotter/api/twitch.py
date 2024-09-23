from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from clipspotter import CLIENT_ID, CLIENT_SECRET
from clipspotter.config import REQUEST_TIMEOUT
from clipspotter.models.category import Category


class TwitchAPI:
    base_url = "https://api.twitch.tv/helix/"

    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        response = requests.post(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()["access_token"]

    def _get_headers(self):
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

    def _get_response(self, url: str, query_params: dict[str, Any] | None) -> list[dict[str, Any]] | None:
        response = requests.get(url, headers=self._get_headers(), params=query_params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json().get("data")

    def get_clips(self, category: Category, set_id: str, days_ago: int, first: int) -> list[dict[str, Any]] | None:
        url = self.base_url + "clips"
        params = {
            "first": first,
            "started_at": (datetime.now(tz=timezone.utc) - timedelta(days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ended_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        cat_id_name = "broadcaster_id" if category == Category.STREAMER else "game_id"
        params[cat_id_name] = set_id
        return self._get_response(url, params)

    def _get_streamer_keys(self, name: str) -> tuple[str | None, str | None, str | None]:
        url = self.base_url + "users"
        query_params = {"login": name}
        data = self._get_response(url, query_params)
        if not data:
            return None, None, None
        return data[0].get("id"), data[0].get("login"), data[0].get("display_name")

    def _get_game_keys(self, name: str) -> tuple[str | None, str | None]:
        url = self.base_url + "games"
        query_params = {"name": name}
        data = self._get_response(url, query_params)
        if not data:
            return None, None
        return data[0].get("id"), data[0].get("name")

    def get_broadcaster_id(self, name: str) -> tuple[str | None, str | None, str | None]:
        return self._get_streamer_keys(name)

    def get_game_id(self, name: str) -> tuple[str | None, str | None]:
        return self._get_game_keys(name)
