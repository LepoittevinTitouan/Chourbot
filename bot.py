# bot.py
import os
import asyncio

import discord

TOKEN = 'NzIzODM2OTExMDE3Mzk0MjM4.Xu3b3w.k4vavWFI3OxXMUsc1Hdv7BOXcUo'

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('_hein'):
        msg = ':heeee: :eeee: :eeee: :eeee: :ein:'.format(message)
        await message.channel.send(msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)
