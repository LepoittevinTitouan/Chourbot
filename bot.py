import os, sys
import time
import random
import discord
from dotenv import load_dotenv

import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

connectedGuild = None
# Load commands

with open('command.json') as f:
    commands = json.load(f)

# Import all callbacks
from callbacks import *

client = discord.Client()


@client.event
async def on_ready():
    global connectedGuild
    for guild in client.guilds:
        if guild.name == GUILD:
            connectedGuild = guild
            break
    print("Ready !")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == "stats-cs":
        await csstats.call(message)

    for command in commands:
        splitedString = message.content.split()

        if splitedString[0] == command["code"]:
            print("Start function :", splitedString[0])

            # Start a function from a string
            possibles = globals().copy()
            possibles.update(locals())
            method = possibles.get(command["callback"])
            if not method:
                raise NotImplementedError("Method %s not implemented" % method)
            await method(message, connectedGuild)


@client.event
async def on_voice_state_update(member, before, after):
    if str(member.id) != "523531083078434819":  # Exclute the bot itself
        if after.channel.name == "Heiiiiiiiiiin" and (before.channel is None or before.channel.name != "Heiiiiiiiiiin"):
            # Join the channel
            print(member, "join the channel HEEEEEEEEEIIIIIIIIIINNNN")

            channel = after.channel
            vc = await channel.connect()

            try:
                vc.play(discord.FFmpegPCMAudio(
                    source='hein.mp3',
                    executable=r'D:\Program Files\ffmpeg\ffmpeg-5.0.1-essentials_build\bin\ffmpeg.exe'),
                    after=lambda x: print('Hein done')
                )
                time.sleep(2)
                await vc.disconnect()

            except Exception as e:
                print(e)
                await vc.disconnect()


client.run(TOKEN)
