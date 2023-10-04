import requests

from contact_service.settings import USER_API_KEY, APP_BASE_URL


def check_friend_status(contacts):
    payload = {
        "contacts": contacts,
    }
    url = f"{APP_BASE_URL}/api/users/user_friends_check/"
    print(url)
    print(payload)
    print(USER_API_KEY)
    print("App User check")
    headers = {"Authorization": f"Api-Key {USER_API_KEY}"}
    result = requests.post(url, json=payload, headers=headers)
    print(result.text)
    if result.status_code == 200:
        return 200, result.json()
    return 400, result.text
