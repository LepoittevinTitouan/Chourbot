import json
import random
import discord
import sqlite3
import time

import rlstats

async def randomNickname(message,guild):
    splitedString = message.content.split(" ",1)
    if len(splitedString)==2 :
        memberId=0
        if splitedString[1].startswith("<@!"):
            # remove 3 first char and last one
            temp = splitedString[1][3:]
            memberId = temp[:-1]

        for member in message.guild.members:
            # If start with @ remove the @
            if (member.name.lower() == splitedString[1].lower()) or (str(member.id) == str(memberId)) or (member.display_name.lower() == splitedString[1].lower()) :
                output = "Renaming "+member.name
                # await message.channel.send(output)
                await message.delete()

                originalName = member.display_name.lower()
                shuffled = list(originalName)
                random.shuffle(shuffled)
                shuffled = ''.join(shuffled)
                shuffled = shuffled.capitalize()
                await member.edit(nick=shuffled,reason="Heeeeeeeeiiiin")
                break;
        else :
            await message.channel.send("User not found")
            pass

    else :
        await message.channel.send("Bad parameters")
        pass

async def resetNickname(message,guild):
    splitedString = message.content.split(" ",1)
    if len(splitedString)==2 :
        memberId=0
        if splitedString[1].startswith("<@!"):
            # remove 3 first char and last one
            temp = splitedString[1][3:]
            memberId = temp[:-1]

        for member in message.guild.members:
            # If start with @ remove the @
            if (member.name.lower() == splitedString[1].lower()) or (str(member.id) == str(memberId)) or (member.display_name.lower() == splitedString[1].lower()) :
                await message.delete()

                # Connect to DB
                conn = sqlite3.connect('users.db')
                c = conn.cursor()

                c.execute("SELECT name, display_name FROM users WHERE id=?",(member.id,))
                values = c.fetchone()

                nickname = values[1]
                oldNickname = member.display_name
                # If current nickname is different than saved nickname
                if oldNickname != nickname :
                    await member.edit(nick=nickname,reason="Heeeeeeeeiiiin")
                    msg = "Reset" + oldNickname + ' :arrow_forward: ' +nickname
                    await message.channel.send(content=msg,delete_after=5)

                break;
        else :
            pass

    else :
        await message.channel.send("Bad parameters")
        pass

async def setNickname(message,guild):
    splitedString = message.content.split()
    if len(splitedString)==3 :
        memberId=0
        if splitedString[1].startswith("<@!"):
            # remove 3 first char and last one
            temp = splitedString[1][3:]
            memberId = temp[:-1]

        for member in message.guild.members:
            # If start with @ remove the @
            if (member.name.lower() == splitedString[1].lower()) or (str(member.id) == str(memberId)) or (member.display_name.lower() == splitedString[1].lower()) :
                await message.delete()
                await member.edit(nick=splitedString[2],reason="Heeeeeeeeiiiin")
                break;
        else :
            await message.channel.send("User not found")
            pass

    else :
        await message.channel.send("Bad parameters")
        pass

async def hein(message,guild):

    splitedString = message.content.split()

    if len(splitedString)==1 :
        # If only $hein
        msg = '<:Heeee:723830564104437841> <:eeee:723833827390128140> <:eeee:723833827390128140> <:eeee:723833827390128140> <:ein:723833854703697921>'.format(message)
        await message.delete()
        await message.channel.send(msg,delete_after=30)



    else :
        # hein on a user in a voice channel
        # $hein @Nyitus
        # or everybody $hein all
        if splitedString[1] == "all" :
            await message.delete()
            # Se connecte a chaque channel où il y a au moins une personne et crie HEEEEIIIINNNN
            channels = guild.voice_channels
            notEmptyChannel = []
            for channel in channels:
                members = channel.members
                if len(members)>=1 :
                    print("Channel :",channel)
                    notEmptyChannel.append(channel)


            for channel in notEmptyChannel:
                vc = await channel.connect()

                try:
                    vc.play(discord.FFmpegPCMAudio('hein.mp3'), after=lambda e: print('Hein', e))
                    time.sleep(2)
                    await vc.disconnect()

                except Exception as e:
                    print(e)
                    await vc.disconnect()
        else :
            memberId=0
            if splitedString[1].startswith("<@!"):
                # remove 3 first char and last one
                # This happens when you @ someone
                temp = splitedString[1][3:]
                memberId = temp[:-1]


            for member in message.guild.members:
                # If start with @ remove the @
                if (member.name.lower() == splitedString[1].lower()) or (str(member.id) == str(memberId)) or (member.display_name.lower() == splitedString[1].lower()) :
                    # User found
                    await message.delete()

                    flag = True
                    # Get all voice channels available
                    channels = guild.voice_channels
                    connectedChannel = None
                    for channel in channels:
                        members = channel.members
                        for memberConnected in members:
                            if memberConnected==member:
                                print("Member found in channel :",channel)
                                flag = False
                                vc = await channel.connect()

                                # PLay HEEEEIIIINNNN
                                try:
                                    vc.play(discord.FFmpegPCMAudio('hein.mp3'), after=lambda e: print('Hein', e))
                                    time.sleep(2)
                                    await vc.disconnect()

                                except Exception as e:
                                    print(e)
                                    await vc.disconnect()
                    if flag:
                        await message.channel.send(content="User not connected in a voice channel",delete_after=5)

async def updateDB(message,guild):

    await message.delete()
    # await message.channel.send("User database updated")


    # Connect to DB
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # delete all rows from table
    c.execute('DELETE FROM users;',);
    conn.commit()

    # Get all members
    members = '\n - '.join([member.display_name for member in guild.members])
    print(f'Guild Members:\n - {members}')



    for member in guild.members:
        c.execute("INSERT INTO users VALUES (?,?,?)",(member.id,member.name,member.display_name))

    conn.commit()
    print("User database updated")



async def resetFromDB(message,guild):
    await message.delete()
    print("resetFromDB Function")

    # Connect to DB
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    msg = "Reset nickname for :"

    # Get difference to only update the users with a difference
    for member in guild.members:
        c.execute("SELECT name, display_name FROM users WHERE id=?",(member.id,))
        values = c.fetchone()

        nickname = values[1]
        oldNickname = member.display_name
        # If current nickname is different than saved nickname
        if member.display_name != nickname :
            await member.edit(nick=nickname,reason="Heeeeeeeeiiiin")
            msg += "\n - " + oldNickname + ' :arrow_forward: ' +nickname

    await message.channel.send(content=msg,delete_after=5)



async def help(message,guild):
    await message.delete()
    print("Help Function")
    # Load commands
    with open('command.json') as f:
      commands = json.load(f)

    msg = "~~~~~~ **Commandes Bot Chourbe** ~~~~~~\n\n"


    for command in commands :
        if command["callback"]!="help":
            if len(command["examples"])==1:
                msg += ' - **'+command["name"]+'**\n'+command["description"]+'\nCommande : `'+command["examples"][0]+"`\n\n"

            if len(command["examples"])>1:
                msg += ' - **'+command["name"]+'**\n'+command["description"]+'\nCommande : '
                for cmd in command["examples"]:
                    msg += "\n        `"+cmd+"`"
                msg += "\n\n"
    await message.channel.send(content=msg)

async def stats(message,guild):
    await rlstats.call(message,guild)
