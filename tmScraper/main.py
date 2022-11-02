import random
import threading
from tmScraper.util import authentication, leaderboard
import json
import time
from datetime import datetime
from tmScraper import settings


def ReadData(file):
    print("Opening data from file (" + file + ")")
    with open(file, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def getCongrats():
    with open('tmScraper/data/congrats_fr.txt', 'r') as f:
        lines = f.readlines()
    return random.choice(tuple(set(lines)))


def convertTime(seconds):
    return "{:02.0f}:{:06.3f}".format(*divmod(seconds, 60))


async def main(guild):
    # init
    players = ReadData('tmScraper/data/players.json')
    maps = ReadData('tmScraper/data/maps.json')
    for textChannel in guild.text_channels:
        if textChannel.name == "trackmania":
            channel = textChannel
            break

    # For each authentified player recorded in the players.json file
    for authPlayer in settings.players:
        player = next((item for item in players["players"] if item["pseudo"] == authPlayer["pseudo"]), None)
        if player is None:
            players['players'].append(
                {
                    "pseudo": authPlayer["pseudo"],
                    "rankings": []
                }
            )
            player = next((item for item in players["players"] if item["pseudo"] == authPlayer["pseudo"]), None)

        playerIndex = players["players"].index(player)

        for track in maps['playlist']:
            url = leaderboard.BuildLeaderboardUrl(track['mapUid'])

            with settings.lockTocken:
                response = leaderboard.CallLeaderboardApi(authPlayer['accessToken'], url)

            if not response:
                continue

            # Chercher si la map est enregistrée chez le joueur
            if track['id'] in [mapID for mapID in [i['id'] for i in player['rankings']]]:
                # Sauvegarde de l'index de la map en question pour le joueur
                trackID = next((i for i, item in enumerate(player["rankings"]) if item["id"] == track['id']), None)
                # Comparer l'ancienne valeur et la nouvelle
                if response["tops"][0]["top"][0]["score"] < player["rankings"][trackID]["score"]:
                    print("New Highscore !!")

                    players["players"][playerIndex]["rankings"][trackID]["score"] = response["tops"][0]["top"][0][
                        "score"]
                    players["players"][playerIndex]["rankings"][trackID]["position"] = \
                    response["tops"][0]["top"][0]["position"]

                    # Féliciter le joueur pour son exploit surhumain
                    score = convertTime(response["tops"][0]["top"][0]["score"]/1000)
                    pos = response["tops"][0]["top"][0]["position"]
                    congrats = getCongrats()
                    members = await guild.query_members(player["pseudo"])
                    msg = congrats.replace("###", members[0].mention)
                    msg += f"Nouveau record sur {track['name']} : **{score}**. Classement mondial : {pos}"
                    await channel.send(content=msg)

            else:
                # ajouter le score actuel comme nouveau record
                players["players"][playerIndex]["rankings"].append({
                    'id': track['id'],
                    'position': response["tops"][0]["top"][0]["position"],
                    'score': response["tops"][0]["top"][0]["score"]
                })

                score = convertTime(response["tops"][0]["top"][0]["score"] / 1000)
                pos = response["tops"][0]["top"][0]["position"]
                members = await guild.query_members(player["pseudo"])
                msg = members[0].mention
                msg += f" : Premier finish sur {track['name']} : **{score}**. Classement mondial : {pos}"
                await channel.send(content=msg)

    with open('tmScraper/data/players.json', 'w') as f:
        json.dump(players, f, indent=4)



if __name__ == "__main__":
    start = time.perf_counter()
    print("Running Zrt Trackmania Cup 2022 Leaderboard Tracker")
    print("Time (UTC): " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

    # Init auth
    for player in settings.players:
        authentication.GetAuthentication(player)

    # refresh auth thread
    authThread = threading.Thread(target=authentication.RefreshRoutine)

    # main thread
    main()

    stop = time.perf_counter()
    print(f"Finished in {stop - start:0.4f} seconds")
