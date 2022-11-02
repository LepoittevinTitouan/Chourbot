import time
import requests
from tmScraper import settings


def GetAuthentication(player):
    url = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
    headers = {
        'Authorization': player['authorization'],
        'Host': 'public-ubiservices.ubi.com',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Content-Length': '0',
        'Ubi-AppId': '86263886-327a-4328-ac69-527f0d20a237',
        'user-agent': 'zrtLeaderboardScrapper'
    }
    result = requests.post(url, headers=headers)

    result = result.json()

    player['pseudo'] = result['nameOnPlatform']

    token = result['ticket']

    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices"
    body = {
        'audience': 'NadeoLiveServices'
    }
    headers = {
        'Host': 'prod.trackmania.core.nadeo.online',
        'authorization': 'ubi_v1 t=' + token,  # Temp token
        'content-type': 'application/json',
        'user-agent': 'zrtLeaderboardScrapper'
    }

    result = requests.post(url, headers=headers, json=body)

    result = result.json()

    player['accessToken'] = result["accessToken"]
    player['refreshToken'] = result["refreshToken"]


def GetTokenRefresh(player):
    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/refresh"
    body = {
        'audience': 'NadeoLiveServices'
    }
    with settings.lockTocken:
        headers = {
            'Host': 'prod.trackmania.core.nadeo.online',
            'Authorization': 'nadeo_v1 t=' + player['refreshToken'],
            'content-type': 'application/json',
            'user-agent': 'zrtLeaderboardScrapper'
        }
        result = requests.post(url, headers=headers, json=body)
        result = result.json()

        player['accessToken'] = result["accessToken"]
        player['refreshToken'] = result["refreshToken"]


def RefreshRoutine():
    while True:
        time.sleep(300)
        for player in settings.players:
            GetTokenRefresh(player)
            print("Token refreshed")
