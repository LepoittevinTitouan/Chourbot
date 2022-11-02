import json
import random
import discord
import time


async def hein(message, guild):
    splitedString = message.content.split()

    if len(splitedString) == 1:
        # If only $hein
        msg = '<:Heeee:723830564104437841> <:eeee:723833827390128140> <:eeee:723833827390128140> <:eeee:723833827390128140> <:ein:723833854703697921>'.format(
            message)
        await message.delete()
        await message.channel.send(msg)


    else:
        # hein on a user in a voice channel
        # $hein @Nyitus
        # or everybody $hein all
        if splitedString[1] == "all":
            await message.delete()
            # Se connecte a chaque channel où il y a au moins une personne et crie HEEEEIIIINNNN
            channels = guild.voice_channels
            notEmptyChannel = []
            for channel in channels:
                members = channel.members
                if len(members) >= 1:
                    print("Channel :", channel)
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
        else:
            memberId = 0
            if splitedString[1].startswith("<@!"):
                # remove 3 first char and last one
                # This happens when you @ someone
                temp = splitedString[1][3:]
                memberId = temp[:-1]

            for member in message.guild.members:
                # If start with @ remove the @
                if (member.name.lower() == splitedString[1].lower()) or (str(member.id) == str(memberId)) or (
                        member.display_name.lower() == splitedString[1].lower()):
                    # User found
                    await message.delete()

                    flag = True
                    # Get all voice channels available
                    channels = guild.voice_channels
                    connectedChannel = None
                    for channel in channels:
                        members = channel.members
                        for memberConnected in members:
                            if memberConnected == member:
                                print("Member found in channel :", channel)
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
                        await message.channel.send(content="User not connected in a voice channel", delete_after=5)


async def help(message, guild):
    await message.delete()
    print("Help Function")
    # Load commands
    with open('command.json') as f:
        commands = json.load(f)

    msg = "~~~~~~ **Commandes Bot Chourbe** ~~~~~~\n\n"

    for command in commands:
        if command["callback"] != "help":
            if len(command["examples"]) == 1:
                msg += ' - **' + command["name"] + '**\n' + command["description"] + '\nCommande : `' + \
                       command["examples"][0] + "`\n\n"

            if len(command["examples"]) > 1:
                msg += ' - **' + command["name"] + '**\n' + command["description"] + '\nCommande : '
                for cmd in command["examples"]:
                    msg += "\n        `" + cmd + "`"
                msg += "\n\n"
    await message.channel.send(content=msg)
