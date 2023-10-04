import requests

from aapooncontact.settings import aapoon_BASE_URL


def call_friend_app(payload):
    url = f"{aapoon_BASE_URL}/api/friends/check/"
    print("++++++++")
    print("friends api")
    print(url)

    headers = {}
    result = requests.post(url, json=payload)
    if result.status_code == 200:
        print("++++++++")
        print("friends api response")
        print(result.json())
        return 200, result.json()
    return 400, result.text
