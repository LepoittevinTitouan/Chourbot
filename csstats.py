import discord
import os
import asyncio
import json

competmaps = ["mirage","inferno","overpass","vertigo","nuke","train","dust2","cache"]
results = ["win","loose","tie"]

async def call(message) :
    values = message.content.split()

    if values[0] == "del" and values[1] not in results :
        await delValue(message,int(values[1]))

    elif values[0] in competmaps :
        if len(values) == 4 :
            await addValue(message)
        elif len(values) > 4 :
            await message.channel.send("Erreur de formatage : Trop de paramètres\nLe format est : Map Resultat MVP Player1,Player2,...")
        else :
            await message.channel.send("Erreur de formatage : Pas assez de paramètres\nLe format est : Map Resultat MVP Player1,Player2,...")

async def addValue(message) :
    values = message.content.split()
    state = True

    map = values[0].lower()
    result = values[1].lower()
    mvp = values[2]
    players = values[3].split(",")
    player_count = len(players)

    flagMVP = False
    flagPlayers = 0

    for player in players :
        if players.count(player) > 1 :
            state = False
            await message.channel.send("Erreur : Un joueur apparait plusieurs fois.")
            break

    if player_count > 5 :
        state = False
        await message.channel.send("Erreur : Il y a trop de joueurs (max 5).")

    if map not in competmaps :
        await message.channel.send("Erreur : Cette map n'existe pas ou n'est pas dans le map pool de la team pro CsGo Chourbe !")
        state = False

    if result not in results :
        await message.channel.send("Erreur : Le resultats doit etre parmis les suivants : Win, Loose, Tie.")
        state = False

    for member in message.guild.members :
        if (member.name.lower() == mvp.lower()) or (member.display_name.lower() == mvp.lower()) :
            mvp = member.name
            flagMVP = True

    if not flagMVP :
        state = False
        await message.channel.send("Erreur : Le MVP n'est pas un joueur de CsGo.")

    for i in range(len(players)) :
        temp = players[i]
        for member in message.guild.members :
            if (member.name.lower() == players[i].lower() or member.display_name.lower() == players[i].lower()) :
                temp = member.name
                flagPlayers += 1
                break
        if temp != players[i] :
                players[i] = temp


    if mvp not in players :
        await message.channel.send("Erreur : Le MVP n'est pas parmis les joueurs O_o")
        state = False

    if flagPlayers != player_count :
        state = False
        await message.channel.send("Erreur : Tout les joueurs n'ont pas été trouvés. ("+ str(players[flagPlayers])+")")

    # Traitement terminé
    if state == True :
        with open('csgo.json') as json_file:
            data = json.load(json_file)

        data["games"] += 1
        nb = data["games"]

        if map not in data["maps"].keys() :
            data["maps"][map] = {}
            data["maps"][map]["wins"]=[]
            data["maps"][map]["losses"]=[]
            data["maps"][map]["ties"]=[]
            data["maps"][map]["mvps"]=[]

        if result == "win" :
            data["maps"][map]["wins"].append(nb)
        elif result == "loose" :
            data["maps"][map]["losses"].append(nb)
        elif result == "tie" :
            data["maps"][map]["ties"].append(nb)

        data["maps"][map]["mvps"].append(mvp)

        for player in players :
            if player not in data["players"].keys() :
                data["players"][player] = {}
                data["players"][player]["mvps"] = []
                data["players"][player]["wins"] = []
                data["players"][player]["losses"] = []
                data["players"][player]["ties"] = []

            if result == "win" :
                data["players"][player]["wins"].append(nb)
            elif result == "loose" :
                data["players"][player]["losses"].append(nb)
            elif result == "tie" :
                data["players"][player]["ties"].append(nb)

            if mvp == player :
                data["players"][player]["mvps"].append(nb)

        with open('csgo.json','w') as outfile:
            json.dump(data,outfile,indent=4)

        await message.channel.send("Nouvelle entrée :\nMap : " + str(map) + "\nResult : " + str(result) + "\nMVP : " + str(mvp) + "\nPlayers : " + str(players) + "\nGame ID : " + str(nb))

async def delValue(message,id):

    with open('csgo.json') as json_file:
        data = json.load(json_file)

    # Bot confirmation
    mapFound = "None"
    resultFound = "None"
    mvpFound = "None"
    playersFound = []

    # Deleting from maps
    for map in data["maps"] :
        for result in data["maps"][map] :
            if id in data["maps"][map][result] :
                data["maps"][map][result].remove(id)
                mapFound = map
                resultFound = result
                break

    # Deleting from players
    for player in data["players"] :
        if id in data["players"][player]["mvps"] :
            mvpFound = player
            data["players"][player]["mvps"].remove(id)

        for key in ["wins","losses","ties"] :
            if id in data["players"][player][key] :
                data["players"][player][key].remove(id)
                playersFound.append(player)

    # Removing the MVP
    if mapFound != "None" and resultFound != "None" and mvpFound != "None":
        data["maps"][mapFound]["mvps"].remove(mvpFound)

        with open('csgo.json','w') as outfile:
            json.dump(data,outfile,indent=4)

        await message.channel.send("Game ID : " + str(id) + " has been removed.\nMap : " + str(mapFound) + "\nResult : " + str(resultFound) + "\nMVP : " + str(mvpFound) + "\nPlayers : " + str(playersFound))

    else :
        await message.channel.send("Game ID : " + str(id) + " already has been removed, or doesn't exist.")

# if __name__ == "__main__":
    # # Creating initial data
    # data = {}
    # data["maps"]={}
    # data["players"]={}
    # data["games"]=0
    # with open('csgo.json', 'w') as outfile:
    #     json.dump(data, outfile,indent=4)

    # # Testing to add data
    # message = "inferno loose Betaking Tits,Nyitus,Keynox,Betaking"
    # addValue(message)

    # # Refactoring looses to losses
    # with open('csgo.json') as json_file:
    #     data = json.load(json_file)
    #
    # list = ["maps","players"]
    # for key1 in list :
    #     for key2 in data[key1] :
    #         data[key1][key2]["losses"] = data[key1][key2].pop("looses")
    #
    # with open('csgo.json', 'w') as outfile:
    #     json.dump(data, outfile,indent=4)
