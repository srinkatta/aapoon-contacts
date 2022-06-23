import requests

from aapooncontact.settings import aapoon_API_KEY, aapoon_BASE_URL


def check_friend_status(phone_number):
    payload = {
        "phone_number": phone_number,
    }
    url = f"{aapoon_BASE_URL}/api/v1/user/check/"

    headers = {"Authorization": f"Api-Key {aapoon_API_KEY}"}
    result = requests.post(url, data=payload, headers=headers)
    if result.status_code == 200:
        return 200, result.json()["friend"]
    return 400, result.text
