import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
import calendar
import discord
import os
import asyncio

def test(message) :
    data = pd.read_csv(message.attachments[0].url)
    print(data)
