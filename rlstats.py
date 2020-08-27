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
    else :
        print (message.author)
