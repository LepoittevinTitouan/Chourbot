# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('NzIzODM2OTExMDE3Mzk0MjM4.Xu3b3w.k4vavWFI3OxXMUsc1Hdv7BOXcUo')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)
