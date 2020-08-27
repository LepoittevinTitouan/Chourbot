import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
import calendar
import discord
import os
import asyncio
from urllib.request import Request, urlopen

async def call(message,guild) :
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

    if  not data.empty :
        # Correcting the DataFrame
        data["Index"] = np.arange(len(data))
        data["Timestamp"] = pd.to_datetime(data["Timestamp"])
        data["Weekday"] = data["Timestamp"].dt.day_name()

        await plot3s(data,message)

        fig = plt.figure()
        ax = plt.axes()

        y = data.loc[data["Playlist"] == "Standard"]
        y = y.loc[y["MMR"] > 200]
        y = y["MMR"].tolist()

        y2 = data.loc[data["Playlist"] == "Doubles"]
        y2 = y2.loc[y2["MMR"] > 200]
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

async def plot3s(data,message):

    #Traitement données :
    #Limitation du nombre de données
    data = data.loc[data["Playlist"] == "Standard"]
    data = data.loc[data["Ranked"] == 1]
    data.tail(50)

    #Selection du MMR avec exclusion des buggés
    mmr3s = data.loc[data["MMR"] > 200]
    mmr3s = mmr3s["MMR"].tolist()

    #Selection du score
    score = data["Score"].tolist()
    scoremean = data["Score"].mean()

    #Selection des MVP
    mvp = data["MVP"].tolist()

    #Fluctuation du MMR
    mmrwin = 0
    mmrloose = 0
    prec = 0
    for i in mmr :
        if not prec :
            prec = i
        elif i > prec :
            mmrwin = mmrwin + (i - prec)
            prec = i
        elif i < prec :
            mmrloose = mmrloose + ( prec - i )
            prec = i
        else :
            prec = 1

    #Préparation du pie chart
    labels = 'Goals','Saves','Assists'
    sizes =[]
    for l in labels :
        myList = data[l].tolist()
        total = sum(myList)
        sizes.append(total)

    # Winrate + win/loose
    winrate = data["Win"].mean()
    winrate = winrate * 100
    win = data["Win"].sum()
    loose = (win * 100 / winrate) - win
    nb = win + loose

    #Affichage %MVP
    mvpMean = data["MVP"].mean()
    mvpMean = mvpMean * 100
    mvpMeanWin = data.loc[data["Win"] == 1]
    mvpMeanWin = mvpMeanWin["MVP"].mean()
    mvpMeanWin = mvpMeanWin * 100


    plt.rc('figure',facecolor='w')
    fig = plt.figure(constrained_layout = True)

    # Use GridSpec for customising layout
    gs = fig.add_gridspec(nrows=7, ncols=6)
    # Add an empty axes that occupied the whole first row
    axTitle = fig.add_subplot(gs[0,:])
    axTitle.annotate('3s Data',(0.5,0.5),
                     xycoords='axes fraction', va='center', ha='center')
    axTitle.get_xaxis().set_visible(False)
    axTitle.get_yaxis().set_visible(False)

    # Plot principal
    axPrincipal = fig.add_subplot(gs[1:2,0:3])

    # Annotation fluctuation
    axFlucPos = fig.add_subplot(gs[1,4:5])
    toShowPositiveMMR = "MMR total gagné : " + str(mmrwin)
    axFlucPos.annotate(toShowPositiveMMR,(0.5,0.5),
                  xycoords='axes fraction',va='center',ha='center')

    # Annotation fluctuation
    axFlucNeg = fig.add_subplot(gs[2,4:5])
    toShowNegativeMMR = "MMR total perdu : " + str(mmrloose)
    axFlucNeg.annotate(toShowNegativeMMR,(0.5,0.5),
                  xycoords='axes fraction',va='center',ha='center')

    # Pie chart
    axPie = fig.add_subplot(gs[3:4,0:1])
    axPie.pie(sizes,labels=labelsautopct='%1.1f%%')
    axPie.axis('equal')

    # Annotation Winrate
    axWinrate = fig.add_subplot(gs[3,2:3])
    winrateper = str(winrate) + "%"
    axWinrate.annotate(winrateper,(0.5,0.5),
                  xycoords='axes fraction',va='center',ha='center')

    # Annotation win & loose
    axWin = fig.add_subplot(gs[4,2])
    winNb = str(win) + "\nWins"
    axWin.annotate(winNb,(0.5,0.5),
                  xycoords='axes fraction',va='center',ha='center')

    axLoose = fig.add_subplot(gs[4,3])
    loosNb = str(loose) + "\nLooses"
    axLoose.annotate(loosNb,(0.5,0.5),
                  xycoords='axes fraction',va='center',ha='center')
