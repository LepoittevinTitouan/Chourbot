import json


async def receiveMessage(message):
    splitedString = message.content.split()

    if splitedString[0] == "$add" and len(splitedString) == 3:
        await addMap(splitedString[1], message.channel, splitedString[2:])

    elif splitedString[0] == "$modify" and len(splitedString) == 4:
        await modifyMap(splitedString[1], splitedString[2], splitedString[3], message.channel)

    elif splitedString[0] == "$del" and len(splitedString) == 2:
        await delMap(splitedString[1], message.channel)

    elif splitedString[0] == "$maps":
        await printMaps(message.channel)

    else:
        print("Not valid call")


async def addMap(mapUid, channel, name):
    with open('tmScraper/data/maps.json', "r") as f:
        maps = json.load(f)

    nameStr = ""
    for n in name:
        nameStr += n + " "
    nameStr = nameStr[:-1]

    maps["maxId"] += 1
    maps["playlist"].append(
        {
            "name": nameStr,
            "id": maps["maxId"],
            "mapUid": mapUid
        }
    )

    with open('tmScraper/data/maps.json', "w") as f:
        json.dump(maps, f, indent=4)

    # Send confirmation message
    msg = f"Added the map {name} to the map playlist. It has id {maps['maxId']}."
    await channel.send(content=msg)


async def modifyMap(id, newName, newMapUid, channel):
    with open('tmScraper/data/maps.json', "r") as f:
        maps = json.load(f)

    index = next((i for i, item in enumerate(maps["playlist"]) if item["id"] == int(id)), None)

    maps["playlist"][index]["name"] = newName
    maps["playlist"][index]["mapUid"] = newMapUid

    with open('tmScraper/data/maps.json', "w") as f:
        json.dump(maps, f, indent=4)

    # Send confirmation message
    msg = f"Modified the map n°{id}. {newName} has been updated in the playlist."
    await channel.send(content=msg)


async def printMaps(channel):
    with open('tmScraper/data/maps.json', "r") as f:
        maps = json.load(f)

    msg = "Map Playlist of ZrT Trackmania Cup 2022\n\n"
    for map in maps["playlist"]:
        msg += " - **" + map["name"] + "** with id " + str(map["id"]) + "\n"

    await channel.send(content=msg)


async def delMap(id, channel):
    with open('tmScraper/data/maps.json', "r") as f:
        maps = json.load(f)

    index = next((i for i, item in enumerate(maps["playlist"]) if item["id"] == int(id)), None)

    maps["playlist"].pop(index)

    with open('tmScraper/data/maps.json', "w") as f:
        json.dump(maps, f, indent=4)

    # Send confirmation message
    msg = f"The map {id} has been deleted. {len(maps['playlist'])} maps in the playlist."
    await channel.send(content=msg)


if __name__ == "__main__":
    addMap('test map', 'wrong uid')

    modifyMap(9, "modified","pareil")