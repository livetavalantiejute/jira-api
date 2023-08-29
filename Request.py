from dataclasses import dataclass
from requests.auth import HTTPBasicAuth
import requests
import sys
import re

import json


@dataclass
class Request:
    headers: dict = None
    username: str = ""
    apikey: str = ""
    url: str = ""
    auth: tuple = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.auth is None:
            self.auth = HTTPBasicAuth(self.username, self.apikey)

    def clean_url(self):
        """Clean url - remove www and add a trailing slash if not present"""
        url = re.sub(r"www.", "", self.url)
        trailing_slash = re.search(r"/$", url)
        if not trailing_slash:
            url = url + "/"
        self.url = url

    def get_user_id(self):
        """Get user id from jira url"""
        query = {
            "query": self.username
        }
        try:
            user_id_response = requests.request(
                "GET",
                self.url+"rest/api/3/user/search",
                headers=self.headers,
                params=query,
                auth=self.auth,
            )
            user_id = user_id_response.json()[0]["accountId"]
        except IndexError:
            sys.exit("No user found.")
        except Exception as e:
            sys.exit(str(e))

        return user_id
