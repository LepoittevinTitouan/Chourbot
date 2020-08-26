# bot.py
import rldata


TOKEN = 'NzIzODM2OTExMDE3Mzk0MjM4.Xu3bpw.Cxd6LXleugMCEUwToWk-ZrhwqtI'
'

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('_hein'):
        msg = '<:heeee:723830564104437841> <:eeee:723833827390128140> <:eeee:723833827390128140> <:eeee:723833827390128140> <:ein:723833854703697921>'.format(message)
        message.delete()
        await message.channel.send(msg)

    if message.content.startswith('_rl'):
        rldata.test(message)

@client.event
async def on_ready():
    pass


client.run(TOKEN)
