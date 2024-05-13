import MetaTrader5 as mt5
from datetime import datetime, timedelta
import matplotlib.  pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import datetime as dt


def initialize_mt5():
    path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    #Old Testing
    login = 124207670
    password = "abcdABCD123!@#"
    server = "Exness-MT5Trial7"

    #new Testing account
    # login = 116363058
    # password = "abcdABCD123!@#"
    # server = "Exness-MT5Trial6"

    timeout = 10000
    portable = False
    if mt5.initialize(path=path, login=login, password=password, server=server, timeout=timeout, portable=portable):
        print("Initialization successful")
    else:
        print('Initialize failed')


def ema(prices):

    ema = prices['close'].ewm(span=20).mean()
    a = ema.shift(1)
    return ema, a



initialize_mt5()