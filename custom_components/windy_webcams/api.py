"""API for Windy."""
from datetime import datetime
from io import BytesIO
from urllib.error import HTTPError

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


def extract_image_preview_url(json_data):
    if 'images' not in json_data:
        return None
    return json_data["images"]["current"]["preview"]

def extract_image_full_url(json_data):
    preview = extract_image_preview_url(json_data)
    if preview is None:
        return None
    return preview.replace('preview', 'full')

def extract_image_last_updated(json_data):
    if 'lastUpdatedOn' in json_data:
        str_value = json_data["lastUpdatedOn"]
        return datetime.fromisoformat(str_value)
    return None


def get_image_bytes(url):
    response = get(url)
    if response.status_code == 404:
        return None
    return BytesIO(response.content).getvalue()
