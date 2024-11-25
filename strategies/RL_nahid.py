# This is a sample Python script.
import time
import math
from datetime import datetime
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from hmmlearn import hmm
import matplotlib.pyplot as plt
import time

from akash import get_avg_candle_size
from xian import take_the_profit, cumulative_lot, create_candle_type_RL
from mt5_utils import get_live_data, initialize_mt5, get_magic_number, trade_order_magic

'''import time
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.




import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters




register_matplotlib_converters()
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from candlestick import candlestick




'''
def calculate_rsi(data, period=14):
    delta = data['close'].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    data['rsi'] = rsi
    return data
def calculate_adx(data, period=14):
    # Calculate the price differences
    data['High-Low'] = data['high'] - data['low']
    data['High-Close'] = np.abs(data['high'] - data['close'].shift(1))
    data['Low-Close'] = np.abs(data['low'] - data['close'].shift(1))

    # Calculate True Range
    data['TR'] = data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)

    # Calculate directional movements
    data['+DM'] = np.where((data['high'] - data['high'].shift(1)) > (data['low'].shift(1) - data['low']),
                           data['high'] - data['high'].shift(1), 0)
    data['+DM'] = np.where(data['+DM'] < 0, 0, data['+DM'])
    data['-DM'] = np.where((data['low'].shift(1) - data['low']) > (data['high'] - data['high'].shift(1)),
                           data['low'].shift(1) - data['low'], 0)
    data['-DM'] = np.where(data['-DM'] < 0, 0, data['-DM'])

    # Calculate smoothed TR, +DM, -DM
    data['TR_smooth'] = data['TR'].rolling(window=period).sum()
    data['+DM_smooth'] = data['+DM'].rolling(window=period).sum()
    data['-DM_smooth'] = data['-DM'].rolling(window=period).sum()

    # Calculate +DI and -DI
    data['+DI'] = 100 * (data['+DM_smooth'] / data['TR_smooth'])
    data['-DI'] = 100 * (data['-DM_smooth'] / data['TR_smooth'])

    # Calculate DX and ADX
    data['DX'] = 100 * np.abs(data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI'])
    data['ADX'] = data['DX'].rolling(window=period).mean()

    # Return the data with ADX values
    return data



def boilinger_bands(df, window=20, num_std=2):

    # Function to calculate Bollinger Bands
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (num_std * df['std_dev'])

    return df

def create_MA(df, window=50):
    df['ma'] = df['close'].rolling(window=window).mean()
    return df



alpha = 0.1                # Learning rate
gamma = 0.9                # Discount factor
epsilon = 0.1              # Exploration rate
num_episodes = 1000
Q_table = {}
actions = ['Hold', 'Buy', 'Sell']
def update_q_table(price_change_buy,price_change_sell,state):
    #initialize_q_table(state)         # Ensure current state exists in Q-table
    initialize_q_table(state)    # Ensure next state exists in Q-table

    # Q-value update using the Q-learning formula
    max_future_q = max(Q_table[state].values())
    reward=2


    action='Buy'
    reward=rewardd(action,price_change_buy,price_change_sell)
    current_q = Q_table[state][action]
    Q_table[state][action] = current_q + alpha * (reward + gamma * max_future_q - current_q)

    action = 'Sell'
    reward = rewardd(action, price_change_buy,price_change_sell)
    current_q = Q_table[state][action]
    Q_table[state][action] = current_q + alpha * (reward + gamma * max_future_q - current_q)

    action = 'Hold'
    reward = rewardd(action, price_change_buy,price_change_sell)
    current_q = Q_table[state][action]
    Q_table[state][action] = current_q + alpha * (reward + gamma * max_future_q - current_q)

def rewardd(action, price_change_buy,price_change_sell):
    if action == 'Buy':
        return price_change_buy  # Positive if price increased after buying
    elif action == 'Sell':
        return price_change_sell # Positive if price decreased after selling
    else:
        return 0

def initialize_q_table(state):
    if state not in Q_table:
        Q_table[state] = {action: 0.0 for action in actions}  # Initialize Q-values to 0.0 for each action

def predict_action(state):
    if state in Q_table:
        # Select action with the highest Q-value
        return max(Q_table[state], key=Q_table[state].get)
    else:
        # Handle unseen states (default to 'Hold' or any fallback strategy)
        print(f"State {state} not found in Q-table. Defaulting to 'Hold'.")
        return 'Hold'


def bot_1(symbol, lot):

    num_candles = 30
    num_prev_can = 1
    num_next_can = 3
    # Number of candles to include in the state
    price_bins = ['Low', 'Medium', 'High']  # Discretized price levels
     # Actions: 0 = Hold, 1 = Buy, 2 = Sell

    # rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M2,
    #                              datetime.now() - timedelta(days=0) - timedelta(minutes=6000),
    #                              datetime.now() - timedelta(days=0))
    #
    # ticks_frame1 = pd.DataFrame(rates)

    time_frame = "M1"
    ticks_frame1 = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=50000)
    print(ticks_frame1.shape)

    ticks_frame1 = calculate_adx(ticks_frame1, period=14)
    ticks_frame1 = calculate_rsi(ticks_frame1)
    ticks_frame1 = boilinger_bands(ticks_frame1)
    ticks_frame1 = create_MA(ticks_frame1)

    ## Candle Type
    ticks_frame1 = create_candle_type_RL(ticks_frame1)
    replace_values = {
        'None': 0,
        'bullish_marubozu': 1,
        'bearish_marubozu': 2,
        'doji': 3,
        'hammer': 4,
        'shooting_star': 5,
        'bearish_hanging_man': 6,
        'bullish_inverted_hammer': 7

    }
    ticks_frame1 = ticks_frame1.replace({"candle_type": replace_values})


    ticks_frame1 = ticks_frame1.fillna(0)
    state = []
    print('hhh')

    max_upper_band = ticks_frame1['upper_band'].max()
    max_lower_band = ticks_frame1['lower_band'].max()
    max_ma = ticks_frame1['ma'].max()

    for i in range(len(ticks_frame1)-num_prev_can-2):
        state=[]
        high_prices = []
        low_prices = []

        for _ in range(i,num_prev_can+i):
            adx=ticks_frame1.iloc[_]['ADX']
            rs=ticks_frame1.iloc[_]['rsi']
            boil_upper_band = round(ticks_frame1.iloc[_]['upper_band'] / max_upper_band, 2)
            boil_lower_band = round(ticks_frame1.iloc[_]['lower_band'] / max_lower_band, 2)
            ma = round(ticks_frame1.iloc[_]['ma'] / max_ma, 2)
            candle_type = ticks_frame1.iloc[_]['candle_type']
            #high_price = ticks_frame1.iloc[_]['open']  # Random high price
            #low_price = ticks_frame1.iloc[_]['close']  # Random low price

            state.append((math.ceil(adx), math.ceil(rs), boil_upper_band, boil_lower_band, ma, candle_type))

        high_prices.append(ticks_frame1.iloc[num_prev_can + i]['high'])
        low_prices.append(ticks_frame1.iloc[num_prev_can + i]['low'])

        high_prices.append(ticks_frame1.iloc[num_prev_can + i + 1]['high'])
        low_prices.append(ticks_frame1.iloc[num_prev_can + i + 1]['low'])

        high_prices.append(ticks_frame1.iloc[num_prev_can + i + 2]['high'])
        low_prices.append(ticks_frame1.iloc[num_prev_can + i + 2]['low'])

        #print(num_prev_can + i,'   ',num_prev_can + i+1,'   ',num_prev_can + i+2)
        price_change_buy=((max(high_prices)-ticks_frame1.iloc[num_prev_can + i]['open'])/ticks_frame1.iloc[num_prev_can + i]['open'])*100
        price_change_sell = ((ticks_frame1.iloc[num_prev_can + i]['open']-min(low_prices))/ticks_frame1.iloc[num_prev_can + i]['open'])*100
        #print(price_change)

        state=tuple(state)
        update_q_table(price_change_buy,price_change_sell, state)

        # print(Q_table)
        # print('-------')
        # print(high_prices)
        # print(low_prices)


    isOneCandle=False
    prev_time = datetime.now().minute

    while True:

        time.sleep(1)
        take_the_profit(symbol)

        # print(prev_time,'    ',cur_time)
        cur_time = datetime.now().minute
        if prev_time == cur_time:
            isOneCandle = False
        else:
            isOneCandle = True
        if (cur_time % 2) == 0 and isOneCandle:

            # rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M2,
            #                              datetime.now() - timedelta(days=0) - timedelta(minutes=600),
            #                              datetime.now() - timedelta(days=0))
            #
            # ticks_frame1 = pd.DataFrame(rates)

            ticks_frame1 = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=500)
            ticks_frame1 = calculate_adx(ticks_frame1, period=14)
            ticks_frame1 = calculate_rsi(ticks_frame1)
            ticks_frame1 = boilinger_bands(ticks_frame1)
            ticks_frame1 = create_MA(ticks_frame1)

            ticks_frame1 = create_candle_type_RL(ticks_frame1)
            replace_values = {
                'None': 0,
                'bullish_marubozu': 1,
                'bearish_marubozu': 2,
                'doji': 3,
                'hammer': 4,
                'shooting_star': 5,
                'bearish_hanging_man': 6,
                'bullish_inverted_hammer': 7

            }
            ticks_frame1 = ticks_frame1.replace({"candle_type": replace_values})

            state = []
            for i in range(1, num_prev_can+1):
                adx = ticks_frame1.iloc[-i]['ADX']
                rs = ticks_frame1.iloc[-i]['rsi']
                boil_upper_band = round(ticks_frame1.iloc[-i]['upper_band'] / max_upper_band, 2)
                boil_lower_band = round(ticks_frame1.iloc[-i]['lower_band'] / max_lower_band, 2)
                ma = round(ticks_frame1.iloc[-i]['ma'] / max_ma, 2)
                candle_type = ticks_frame1.iloc[-i]['candle_type']

                state.append((math.ceil(adx), math.ceil(rs), boil_upper_band, boil_lower_band, ma, candle_type))


            state = tuple(state)
            pred = predict_action(state)
            print(pred)
            print('------------------------------------------')
            prev_time = cur_time

            ## START TRADE
            action = None
            if pred == 'Sell':
                action = 'sell'
            elif pred == 'Buy':
                action = 'buy'

            if action:  # action and
                lot = cumulative_lot()
                tp = 3000
                sl = 1000

                tp_multi = 1.5
                sl_multi = 1

                if tp is None:
                    return
                avg_candle_size, sl, tp = get_avg_candle_size(symbol, ticks_frame1, tp_multi, sl_multi)

                MAGIC_NUMBER = get_magic_number()
                trade_order_magic(symbol=symbol, tp_point=tp, sl_point=sl, lot=lot, action=action, magic=True,
                                  code=911,
                                  MAGIC_NUMBER=MAGIC_NUMBER)


    #positions = mt5.positions_get(symbol=symbol)
    #print(ticks_frame1)
    # Discretization function for high and low prices

    # Initialize state with random high and low prices for the last 10 candles



    # Convert state to tuple to make it hashable


    # Initialize Q-table as a dictionary with default Q-values for each action


    # Function to initialize Q-values for a given state if it doesn't exist


    # Initialize Q-table for the generated state
    initialize_q_table(state)

    # Display the Q-table entry for the current state
    print("Q-table entry for the initialized state:")
    # print(f"State: {state}")
    # for action, q_value in Q_table[state].items():
    #     print(f"  Action: {action}, Q-value: {q_value}")



def Mt5_backTest(muldhon, Current_time, window, totalTime):
    initialize_mt5()

    bot_1('XAUUSD', 0.01)


    mt5.shutdown()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Mt5()
    Mt5_backTest(5000, datetime.now() - timedelta(days=0.5), 60, timedelta(minutes=120))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/




