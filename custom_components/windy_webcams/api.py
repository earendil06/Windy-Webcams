"""API for Windy."""
from datetime import datetime
from io import BytesIO

from requests import get

HOST = "https://api.windy.com"
ENDPOINT = "/webcams/api/v3/webcams/"


def get_webcam_json_data(webcam_id, api_key):
    """Returns json data for specific webcam ID."""
    data = get(
        HOST + ENDPOINT + webcam_id,
        params={"lang": "en", "include": "images"},
        headers={"x-windy-api-key": api_key},
        timeout=15
    ).json()
    return data


def get_image_url(json_data):
    return json_data["images"]["current"]["preview"]

def get_image_last_updated(json_data):
    str_value = json_data["lastUpdatedOn"]
    return datetime.fromisoformat(str_value)


def get_image_bytes(url):
    response = get(url)
    return BytesIO(response.content)
