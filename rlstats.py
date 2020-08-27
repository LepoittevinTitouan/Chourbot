import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
import calendar
import discord
import os
import asyncio
from urllib.request import Request, urlopen

def test(message,guild) :
    if message.attachments :
        req = Request(message.attachments[0].url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0')
        content = urlopen(req)
        data = pd.read_csv(content)
        user = message.author
        filename = str(user) + '.csv'
        data.to_csv(filename)
        print("\nSaved file " + filename +" !")
    else :
        user = message.author
        filename = str(user) + '.csv'
        try :
            data = pd.read_csv(filename)
        except IOError as e:
            print(e)

    if  data :
        data["Index"] = np.arange(len(data))

        fig = plt.figure()
        ax = plt.axes()

        y = data.loc[data["Playlist"] == "Standard"]
        y = y["MMR"].tolist()

        y2 = data.loc[data["Playlist"] == "Doubles"]
        y2 = y2["MMR"].tolist()

        ax.set_xlabel('Nombre de parties')
        ax.set_ylabel('MMR')
        ax.tick_params(axis='y')

        line1, = ax.plot(y, label = "3s",zorder = 10,color = "red")
        line2, = ax.plot(y2, label = "2s")

        fig.tight_layout()

        ax.legend()

        fig.savefig('fig1.png')

        file = discord.File('fig1.png')
        embed = discord.Embed()
        embed.set_image(url="attachment://fig1.png")
        await message.channel.send(file=file,embed=embed)
