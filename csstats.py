import discord
import os
import asyncio
import json

competmaps = ["mirage","inferno","overpass","vertigo","nuke","train","dust2","cache"]
results = ["win","loose","tie"]

async def addValue(message) :
    values = message.content.split()
    # values = message.split()
    map = values[0].lower()
    result = values[1].lower()
    mvp = values[2]
    players = values[3].split(",")
    player_count = len(players)

    state = True
    flagMVP = False
    flagPlayers = 0

    if message.author.name == "Freakyguy" :
        state = False
        await message.channel.send("Erreur : Léo arrête ça je vais te pulver !")

    for player in players :
        if players.count(player) > 1 :
            state = False
            await message.channel.send("Erreur : Un joueur apparait plusieurs fois.")
            break

    if player_count > 4 :
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
            data["maps"][map]["looses"]=[]
            data["maps"][map]["ties"]=[]
            data["maps"][map]["mvps"]=[]

        if result == "win" :
            data["maps"][map]["wins"].append(nb)
        elif result == "loose" :
            data["maps"][map]["looses"].append(nb)
        elif result == "tie" :
            data["maps"][map]["ties"].append(nb)

        data["maps"][map]["mvps"].append(mvp)

        for player in players :
            if player not in data["players"].keys() :
                data["players"][player] = {}
                data["players"][player]["mvps"] = []
                data["players"][player]["wins"] = []
                data["players"][player]["looses"] = []
                data["players"][player]["ties"] = []

            if result == "win" :
                data["players"][player]["wins"].append(nb)
            elif result == "loose" :
                data["players"][player]["looses"].append(nb)
            elif result == "tie" :
                data["players"][player]["ties"].append(nb)

            if mvp == player :
                data["players"][player]["mvps"].append(nb)

        with open('csgo.json','w') as outfile:
            json.dump(data,outfile,indent=4)

        await message.channel.send("Nouvelle entrée :\nMap : " + str(map) + "\nResult : " + str(result) + "\nMVP : " + str(mvp) + "\nPlayers : " + str(players))



if __name__ == "__main__":
    # creating initial data
    data = {}
    data["maps"]={}
    data["players"]={}
    data["games"]=0
    with open('csgo.json', 'w') as outfile:
        json.dump(data, outfile,indent=4)

    # # Testing to add data
    # message = "inferno loose Betaking Tits,Nyitus,Keynox,Betaking"
    # addValue(message)
