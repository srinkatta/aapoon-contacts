import requests

from aapooncontact.settings import aapoon_BASE_URL


def call_friend_app(payload):
    url = f"{aapoon_BASE_URL}/api/friends/check/"

    headers = {}
    result = requests.post(url, data=payload, headers=headers)
    if result.status_code == 200:
        return 200, result.json()
    return 400, result.text
