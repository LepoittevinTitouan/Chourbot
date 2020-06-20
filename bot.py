# bot.py
import os

import discord

TOKEN = 'NzIzODM2OTExMDE3Mzk0MjM4.Xu3b3w.k4vavWFI3OxXMUsc1Hdv7BOXcUo'

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
