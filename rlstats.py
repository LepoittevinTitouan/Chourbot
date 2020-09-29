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

        if "3s" in message.content :
            await plot3s(data,message)
        elif "2s" in message.content :
            await plot2s(data,message)
        elif "1s" in message.content :
            await plot1s(data,message)
        else :
            await plotRecap(data,message)

async def plotRecap(data,message):

    data = data.loc[data["Ranked"] == 1]
    if data.empty :
        await message.channel.send("No available data in " + str(message.author) + "' saved file.")
        return

    mmr3s = data.loc[data["Playlist"] == "Standard"]
    mmr3s = mmr3s.loc[mmr3s["MMR"] > 200]
    mmr3s = mmr3s["MMR"].tolist()

    mmr2s = data.loc[data["Playlist"] == "Doubles"]
    mmr2s = mmr2s.loc[mmr2s["MMR"] > 200]
    mmr2s = mmr2s["MMR"].tolist()

    fig = plt.figure()
    ax = plt.axes()

    ax.set_xlabel('Nombre de parties')
    ax.set_ylabel('MMR')
    ax.tick_params(axis='y')

    line1, = ax.plot(mmr3s, label = "3s",zorder = 10,color = "red")
    line2, = ax.plot(mmr2s, label = "2s")

    fig.tight_layout()

    ax.legend()

    fig.savefig('fig1.png')

    file = discord.File('fig1.png')
    embed = discord.Embed()
    embed.set_image(url="attachment://fig1.png")
    await message.channel.send("Précision en spécifiant '2s' ou '3s' dans la commande !")
    await message.channel.send(file=file,embed=embed)

async def plot3s(data,message):

    #Traitement données :
    #Limitation du nombre de données
    data = data.loc[data["Playlist"] == "Standard"]
    data = data.loc[data["Ranked"] == 1]

    if len(message.content.split()) > 2 :
        dt = datetime.strptime(message.content.split()[2], '%Y-%m-%d')
        data = data.loc[data["Timestamp"] > dt]

    if data.empty :
        await message.channel.send("No game played in 3s in " + str(message.author) + "' saved file.")
        return

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
    for i in mmr3s :
        if not prec :
            prec = i
        elif i > prec :
            mmrwin = mmrwin + (i - prec)
            prec = i
        elif i < prec :
            mmrloose = mmrloose + ( prec - i )
            prec = i
        else :
            prec = i

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

    goalsTot = sum(data['Goals'].tolist())/nb
    savesTot = sum(data['Saves'].tolist())/nb

    #Affichage %MVP
    mvpMean = data["MVP"].mean()
    mvpMean = mvpMean * 100
    mvpMeanWin = data.loc[data["Win"] == 1]
    mvpMeanWin = mvpMeanWin["MVP"].mean()
    mvpMeanWin = mvpMeanWin * 100

    #Best day & best hour
    days = data.groupby("Weekday").mean()
    bDay = days["Win"].idxmax()
    bDayWinrate = days["Win"].max()
    bDayWinrate = bDayWinrate * 100

    data["Rounded"] = data["Timestamp"].dt.round('H')
    data["Rounded"] = data["Rounded"].dt.time
    hours = data.groupby("Rounded").mean()
    bHour = hours["Win"].idxmax()
    bHourWinrate = hours["Win"].max()
    bHourWinrate = bHourWinrate * 100


    # -- PLOT --
    plt.rc('figure',facecolor='xkcd:greyblue')
    fig = plt.figure(constrained_layout = True)
    # Use GridSpec for customising layout
    gs = fig.add_gridspec(nrows=7, ncols=6)
    # Add an empty axes that occupied the whole first row
    axTitle = fig.add_subplot(gs[0,:])
    axTitle.text(0.5,0.5,'3s Data',va='center', ha='center')
    axTitle.axis("off")

    # Plot principal
    axPrincipal = fig.add_subplot(gs[1:3,0:4])
    line1, = axPrincipal.plot(mmr3s,label = "3s")

    # Annotation fluctuation
    axFlucPos = fig.add_subplot(gs[1,4:6])
    toShowPositiveMMR = "MMR total gagné :\n" + str(mmrwin)
    axFlucPos.text(0.5,0.5,toShowPositiveMMR,va='center',ha='center')
    axFlucPos.axis("off")

    # Annotation fluctuation
    axFlucNeg = fig.add_subplot(gs[2,4:6])
    toShowNegativeMMR = "MMR total perdu :\n" + str(mmrloose)
    axFlucNeg.text(0.5,0.5,toShowNegativeMMR,va='center',ha='center')
    axFlucNeg.axis("off")

    # Pie chart
    axPie = fig.add_subplot(gs[3:5,0:2])
    axPie.pie(sizes,labels=labels,autopct='%d%%')
    axPie.axis('equal')

    # Annotation Winrate
    axWinrate = fig.add_subplot(gs[3,2:4])
    winrateper = "Winrate :\n" + str(int(winrate)) + "%"
    axWinrate.text(0.5,0.5,winrateper,va='center',ha='center')
    axWinrate.axis("off")

    # Annotation win & loose
    axWin = fig.add_subplot(gs[4,2])
    winNb = str(int(win)) + "\nWins"
    axWin.text(0.5,0.5,winNb,va='center',ha='center')
    axWin.axis("off")

    axLoose = fig.add_subplot(gs[4,3])
    loosNb = str(int(loose)) + "\nLooses"
    axLoose.text(0.5,0.5,loosNb,va='center',ha='center')
    axLoose.axis("off")

    # Annotation nombre goals shots
    axTot = fig.add_subplot(gs[3,4:6])
    goalsSavesTot = "Total Goals : " + str(round(goalsTot,2)) + "\nTotal Saves : " + str(round(savesTot,2))
    axTot.text(0.5,0.5,goalsSavesTot,va='center',ha='center')
    axTot.axis("off")

    # Annotation nb de parties
    axNb = fig.add_subplot(gs[4,4:6])
    nbParties = str(int(nb)) + "\nParties jouées"
    axNb.text(0.5,0.5,nbParties,va='center',ha='center')
    axNb.axis("off")

    # Affichage %MVP
    axMVP = fig.add_subplot(gs[5:7,0:4])
    axMVP.barh([0,1],[100, 100],color = "grey")
    axMVP.barh([0,1],[mvpMeanWin, mvpMean],color = "blue")
    axMVP.axis("off")

    #Emplacement annotations : x = 75 et y = 1 et 0
    axMVP.annotate(str(int(mvpMean)) + " % of total games", (75,1),va='center',ha='center')
    axMVP.annotate(str(int(mvpMeanWin)) + " % of total wins",(75,0),va='center',ha='center')

    #Best day
    axBestDay = fig.add_subplot(gs[5,4:6])
    bDayString = "Best day :\n" + str(bDay) + " (" + str(int(bDayWinrate)) + "%)"
    axBestDay.text(0.5,0.5,bDayString,va='center',ha='center')
    axBestDay.axis("off")

    #Best hour
    axBestHour = fig.add_subplot(gs[6,4:6])
    bHourString = "Best hour :\n" + str(bHour) + " (" + str(int(bHourWinrate)) + "%)"
    axBestHour.text(0.5,0.5,bHourString,va='center',ha='center')
    axBestHour.axis("off")

    # Saving and sending the file
    fig.savefig('fig1.png')

    file = discord.File('fig1.png')
    embed = discord.Embed()
    embed.set_image(url="attachment://fig1.png")
    await message.channel.send(file=file,embed=embed)

async def plot2s(data,message):

    #Traitement données :
    #Limitation du nombre de données
    data = data.loc[data["Playlist"] == "Doubles"]
    data = data.loc[data["Ranked"] == 1]

    if len(message.content.split()) > 2 :
        dt = datetime.strptime(message.content.split()[2], '%Y-%m-%d')
        data = data.loc[data["Timestamp"] > dt]

    if data.empty :
        await message.channel.send("No game played in 2s in " + str(message.author) + "' saved file.")
        return

    #Selection du MMR avec exclusion des buggés
    mmr2s = data.loc[data["MMR"] > 200]
    mmr2s = mmr2s["MMR"].tolist()

    #Selection du score
    score = data["Score"].tolist()
    scoremean = data["Score"].mean()

    #Selection des MVP
    mvp = data["MVP"].tolist()

    #Fluctuation du MMR
    mmrwin = 0
    mmrloose = 0
    prec = 0
    for i in mmr2s :
        if not prec :
            prec = i
        elif i > prec :
            mmrwin = mmrwin + (i - prec)
            prec = i
        elif i < prec :
            mmrloose = mmrloose + ( prec - i )
            prec = i
        else :
            prec = i

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

    goalsTot = sum(data['Goals'].tolist())/nb
    savesTot = sum(data['Saves'].tolist())/nb

    #Affichage %MVP
    mvpMean = data["MVP"].mean()
    mvpMean = mvpMean * 100
    mvpMeanWin = data.loc[data["Win"] == 1]
    mvpMeanWin = mvpMeanWin["MVP"].mean()
    mvpMeanWin = mvpMeanWin * 100

    #Best day & best hour
    days = data.groupby("Weekday").mean()
    bDay = days["Win"].idxmax()
    bDayWinrate = days["Win"].max()
    bDayWinrate = bDayWinrate * 100

    data["Rounded"] = data["Timestamp"].dt.round('H')
    data["Rounded"] = data["Rounded"].dt.time
    hours = data.groupby("Rounded").mean()
    bHour = hours["Win"].idxmax()
    bHourWinrate = hours["Win"].max()
    bHourWinrate = bHourWinrate * 100


    # -- PLOT --
    plt.rc('figure',facecolor='xkcd:greyblue')
    fig = plt.figure(constrained_layout = True)
    # Use GridSpec for customising layout
    gs = fig.add_gridspec(nrows=7, ncols=6)
    # Add an empty axes that occupied the whole first row
    axTitle = fig.add_subplot(gs[0,:])
    axTitle.text(0.5,0.5,'2s Data',va='center', ha='center')
    axTitle.axis("off")

    # Plot principal
    axPrincipal = fig.add_subplot(gs[1:3,0:4])
    line1, = axPrincipal.plot(mmr2s,label = "2s")

    # Annotation fluctuation
    axFlucPos = fig.add_subplot(gs[1,4:6])
    toShowPositiveMMR = "MMR total gagné :\n" + str(mmrwin)
    axFlucPos.text(0.5,0.5,toShowPositiveMMR,va='center',ha='center')
    axFlucPos.axis("off")

    # Annotation fluctuation
    axFlucNeg = fig.add_subplot(gs[2,4:6])
    toShowNegativeMMR = "MMR total perdu :\n" + str(mmrloose)
    axFlucNeg.text(0.5,0.5,toShowNegativeMMR,va='center',ha='center')
    axFlucNeg.axis("off")

    # Pie chart
    axPie = fig.add_subplot(gs[3:5,0:2])
    axPie.pie(sizes,labels=labels,autopct='%d%%')
    axPie.axis('equal')

    # Annotation Winrate
    axWinrate = fig.add_subplot(gs[3,2:4])
    winrateper = "Winrate :\n" + str(int(winrate)) + "%"
    axWinrate.text(0.5,0.5,winrateper,va='center',ha='center')
    axWinrate.axis("off")

    # Annotation win & loose
    axWin = fig.add_subplot(gs[4,2])
    winNb = str(int(win)) + "\nWins"
    axWin.text(0.5,0.5,winNb,va='center',ha='center')
    axWin.axis("off")

    axLoose = fig.add_subplot(gs[4,3])
    loosNb = str(int(loose)) + "\nLooses"
    axLoose.text(0.5,0.5,loosNb,va='center',ha='center')
    axLoose.axis("off")

    # Annotation nombre goals shots
    axTot = fig.add_subplot(gs[3,4:6])
    goalsSavesTot = "Total Goals : " + str(round(goalsTot,2)) + "\nTotal Saves : " + str(round(savesTot,2))
    axTot.text(0.5,0.5,goalsSavesTot,va='center',ha='center')
    axTot.axis("off")

    # Annotation nb de parties
    axNb = fig.add_subplot(gs[4,4:6])
    nbParties = str(int(nb)) + "\nParties jouées"
    axNb.text(0.5,0.5,nbParties,va='center',ha='center')
    axNb.axis("off")

    # Affichage %MVP
    axMVP = fig.add_subplot(gs[5:7,0:4])
    axMVP.barh([0,1],[100, 100],color = "grey")
    axMVP.barh([0,1],[mvpMeanWin, mvpMean],color = "blue")
    axMVP.axis("off")

    #Emplacement annotations : x = 75 et y = 1 et 0
    axMVP.annotate(str(int(mvpMean)) + " % of total games", (75,1),va='center',ha='center')
    axMVP.annotate(str(int(mvpMeanWin)) + " % of total wins",(75,0),va='center',ha='center')

    #Best day
    axBestDay = fig.add_subplot(gs[5,4:6])
    bDayString = "Best day :\n" + str(bDay) + " (" + str(int(bDayWinrate)) + "%)"
    axBestDay.text(0.5,0.5,bDayString,va='center',ha='center')
    axBestDay.axis("off")

    #Best hour
    axBestHour = fig.add_subplot(gs[6,4:6])
    bHourString = "Best hour :\n" + str(bHour) + " (" + str(int(bHourWinrate)) + "%)"
    axBestHour.text(0.5,0.5,bHourString,va='center',ha='center')
    axBestHour.axis("off")

    # Saving and sending the file
    fig.savefig('fig1.png')

    file = discord.File('fig1.png')
    embed = discord.Embed()
    embed.set_image(url="attachment://fig1.png")
    await message.channel.send(file=file,embed=embed)

async def plot1s(data,message):

    #Traitement données :
    #Limitation du nombre de données
    data = data.loc[data["Playlist"] == "Duel"]
    data = data.loc[data["Ranked"] == 1]

    if len(message.content.split()) > 2 :
        dt = datetime.strptime(message.content.split()[2], '%Y-%m-%d')
        data = data.loc[data["Timestamp"] > dt]

    if data.empty :
        await message.channel.send("No game played in 1s in " + str(message.author) + "' saved file.")
        return

    #Selection du MMR avec exclusion des buggés
    mmr1s = data.loc[data["MMR"] > 200]
    mmr1s = mmr1s["MMR"].tolist()

    #Selection du score
    score = data["Score"].tolist()
    scoremean = data["Score"].mean()

    #Selection des MVP
    mvp = data["MVP"].tolist()

    #Fluctuation du MMR
    mmrwin = 0
    mmrloose = 0
    prec = 0
    for i in mmr1s :
        if not prec :
            prec = i
        elif i > prec :
            mmrwin = mmrwin + (i - prec)
            prec = i
        elif i < prec :
            mmrloose = mmrloose + ( prec - i )
            prec = i
        else :
            prec = i

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

    goalsTot = sum(data['Goals'].tolist())/nb
    savesTot = sum(data['Saves'].tolist())/nb

    #Best day & best hour
    days = data.groupby("Weekday").mean()
    bDay = days["Win"].idxmax()
    bDayWinrate = days["Win"].max()
    bDayWinrate = bDayWinrate * 100

    data["Rounded"] = data["Timestamp"].dt.round('H')
    data["Rounded"] = data["Rounded"].dt.time
    hours = data.groupby("Rounded").mean()
    bHour = hours["Win"].idxmax()
    bHourWinrate = hours["Win"].max()
    bHourWinrate = bHourWinrate * 100


    # -- PLOT --
    plt.rc('figure',facecolor='xkcd:greyblue')
    fig = plt.figure(constrained_layout = True)
    # Use GridSpec for customising layout
    gs = fig.add_gridspec(nrows=7, ncols=6)
    # Add an empty axes that occupied the whole first row
    axTitle = fig.add_subplot(gs[0,:])
    axTitle.text(0.5,0.5,'1s Data',va='center', ha='center')
    axTitle.axis("off")

    # Plot principal
    axPrincipal = fig.add_subplot(gs[1:3,0:4])
    line1, = axPrincipal.plot(mmr1s,label = "1s")

    # Annotation fluctuation
    axFlucPos = fig.add_subplot(gs[1,4:6])
    toShowPositiveMMR = "MMR total gagné :\n" + str(mmrwin)
    axFlucPos.text(0.5,0.5,toShowPositiveMMR,va='center',ha='center')
    axFlucPos.axis("off")

    # Annotation fluctuation
    axFlucNeg = fig.add_subplot(gs[2,4:6])
    toShowNegativeMMR = "MMR total perdu :\n" + str(mmrloose)
    axFlucNeg.text(0.5,0.5,toShowNegativeMMR,va='center',ha='center')
    axFlucNeg.axis("off")

    # Pie chart
    axPie = fig.add_subplot(gs[3:5,0:2])
    axPie.pie(sizes,labels=labels,autopct='%d%%')
    axPie.axis('equal')

    # Annotation Winrate
    axWinrate = fig.add_subplot(gs[3,2:4])
    winrateper = "Winrate :\n" + str(int(winrate)) + "%"
    axWinrate.text(0.5,0.5,winrateper,va='center',ha='center')
    axWinrate.axis("off")

    # Annotation win & loose
    axWin = fig.add_subplot(gs[4,2])
    winNb = str(int(win)) + "\nWins"
    axWin.text(0.5,0.5,winNb,va='center',ha='center')
    axWin.axis("off")

    axLoose = fig.add_subplot(gs[4,3])
    loosNb = str(int(loose)) + "\nLooses"
    axLoose.text(0.5,0.5,loosNb,va='center',ha='center')
    axLoose.axis("off")

    # Annotation nombre goals shots
    axTot = fig.add_subplot(gs[3,4:6])
    goalsSavesTot = "Total Goals : " + str(round(goalsTot,2)) + "\nTotal Saves : " + str(round(savesTot,2))
    axTot.text(0.5,0.5,goalsSavesTot,va='center',ha='center')
    axTot.axis("off")

    # Annotation nb de parties
    axNb = fig.add_subplot(gs[4,4:6])
    nbParties = str(int(nb)) + "\nParties jouées"
    axNb.text(0.5,0.5,nbParties,va='center',ha='center')
    axNb.axis("off")

    #Best day
    axBestDay = fig.add_subplot(gs[5,4:6])
    bDayString = "Best day :\n" + str(bDay) + " (" + str(int(bDayWinrate)) + "%)"
    axBestDay.text(0.5,0.5,bDayString,va='center',ha='center')
    axBestDay.axis("off")

    #Best hour
    axBestHour = fig.add_subplot(gs[6,4:6])
    bHourString = "Best hour :\n" + str(bHour) + " (" + str(int(bHourWinrate)) + "%)"
    axBestHour.text(0.5,0.5,bHourString,va='center',ha='center')
    axBestHour.axis("off")

    # Saving and sending the file
    fig.savefig('fig1.png')

    file = discord.File('fig1.png')
    embed = discord.Embed()
    embed.set_image(url="attachment://fig1.png")
    await message.channel.send(file=file,embed=embed)
