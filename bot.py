import os,sys
import time
import random
import discord
import sqlite3
from dotenv import load_dotenv

import csstats

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


burgerMembers = []
connectedGuild = None
# Load commands
import json
with open('command.json') as f:
  commands = json.load(f)

# Import all callbacks
from callbacks import *


# Connect to DB
conn = sqlite3.connect('users.db')
c = conn.cursor()
try :
    # Create table
    c.execute('''CREATE TABLE users
                 (id text, name text, display_name text)''')
    conn.commit()
except:
    print("Table already created")



client = discord.Client()

@client.event
async def on_ready():
    global connectedGuild,burgerMembers
    for guild in client.guilds:
        if guild.name == GUILD:
            connectedGuild=guild
            break

    # burgerRole = guild.roles
    # print("Burger :",burgerRole)
    burgerRole = guild.get_role(730562433365835857)
    burgerMembers = burgerRole.members

    print("\nOnline burger member :")
    for member in burgerMembers:
        if member.status != discord.Status.offline:
            print(member.display_name)


    # Get all members
    # members = '\n - '.join([member.display_name for member in guild.members])
    # print(f'Guild Members:\n - {members}')

    print("Ready !")
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == "stats-cs":
        await csstats.addValue(message)

    for command in commands:
        splitedString = message.content.split()

        if splitedString[0] == command["code"]:
            print("Start function :",splitedString[0])

            # Start a function from a string
            possibles = globals().copy()
            possibles.update(locals())
            method = possibles.get(command["callback"])
            if not method:
                 raise NotImplementedError("Method %s not implemented" % method_name)
            await method(message,connectedGuild)


@client.event
async def on_voice_state_update(member,before,after):
    if  str(member.id)!="523531083078434819": # Exclute the bot itself
        if (after.channel.name=="Heiiiiiiiiiin" and (before.channel==None or before.channel.name!="Heiiiiiiiiiin")):
            # Join the channel
            print(member,"join the channel HEEEEEEEEEIIIIIIIIIINNNN")


            channel = after.channel
            vc = await channel.connect()

            try:
                vc.play(discord.FFmpegPCMAudio('hein.mp3'), after=lambda e: print('Hein done'))
                time.sleep(2)
                await vc.disconnect()

            except Exception as e:
                print(e)
                await vc.disconnect()


client.run(TOKEN)
