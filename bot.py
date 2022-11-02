import os
import threading

import discord.ext.commands
from dotenv import load_dotenv
from tmScraper.settings import players
import tmScraper.util.authentication as auth
from tmScraper.main import main as scraper
from tmScraper.util import mapManager
from discord.ext import tasks
from discord.ext import commands as com
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

client = com.Bot("$")


@client.event
async def on_ready():
    global connectedGuild
    for guild in client.guilds:
        if guild.name == GUILD:
            connectedGuild = guild
            break
    print("Ready !")

    print("Running Zrt Trackmania Cup 2022 Leaderboard Tracker")

    # Auth players to TM
    for player in players:
        auth.GetAuthentication(player)

    # refresh auth thread
    authThread = threading.Thread(target=auth.RefreshRoutine)
    authThread.start()


class MyCog(com.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.scrap.start()

    def cog_unload(self):
        self.scrap.cancel()

    @tasks.loop(seconds=30.0)
    async def scrap(self):
        print("Running Scraper")
        await scraper(connectedGuild)

    @scrap.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == "trackmania":
        if message.content.startswith('$'):
            await mapManager.receiveMessage(message)

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

client.add_cog(MyCog(client))
client.run(TOKEN)
