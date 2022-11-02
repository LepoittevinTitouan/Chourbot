import requests


def BuildLeaderboardUrl(mapCode):
    baseUrl = "https://live-services.trackmania.nadeo.live/api/token/leaderboard/group/Personal_Best/map/"
    url = baseUrl + mapCode + "/surround/0/0?onlyWorld=true"
    return url


def CallLeaderboardApi(auth, url):
    headers = {
        'Host': 'live-services.trackmania.nadeo.live',
        'Authorization': 'nadeo_v1 t=' + auth,
        'user-agent': 'zrtLeaderboardScrapper'
    }
    result = requests.get(url, headers=headers)

    return result.json()

