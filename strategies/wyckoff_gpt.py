import pandas as pd
import numpy as np


# Function to download forex data from Yahoo Finance
from mt5_utils import initialize_mt5, get_live_data


def get_forex_data(pair, period=10000, interval="D1"):
    data = get_live_data(symbol=pair, time_frame=interval, prev_n_candles=period)
    return data


# Function to identify Wyckoff market phases (basic version)
def identify_market_phases(df):
    df['50_MA'] = df['close'].rolling(window=50).mean()
    df['200_MA'] = df['close'].rolling(window=200).mean()
    df['Volume_Avg'] = df['tick_volume'].rolling(window=50).mean()

    # Identify Wyckoff phases (simplified rules)
    conditions = [
        (df['close'] > df['50_MA']) & (df['50_MA'] > df['200_MA']),  # Markup
        (df['close'] < df['50_MA']) & (df['50_MA'] > df['200_MA']),  # Accumulation
        (df['close'] > df['50_MA']) & (df['50_MA'] < df['200_MA']),  # Distribution
        (df['close'] < df['50_MA']) & (df['50_MA'] < df['200_MA'])  # Markdown
    ]

    phase_labels = ['Markup', 'Accumulation', 'Distribution', 'Markdown']
    df['Market_Phase'] = np.select(conditions, phase_labels, default='Unknown')

    return df


# Function to place trades based on Wyckoff market phase
def trade_with_wyckoff(df, initial_balance=10000):
    balance = initial_balance
    position = 0  # 0 means no position, 1 means long, -1 means short
    for i in range(1, len(df)):
        current_phase = df['Market_Phase'].iloc[i]
        previous_phase = df['Market_Phase'].iloc[i - 1]

        # Trade decision based on phase change
        if current_phase == 'Markup' and position == 0:
            position = 1  # Go long
            print(f"Buy on {df.index[i]}, Price: {df['close'].iloc[i]}")
            balance -= df['close'].iloc[i]

        elif current_phase == 'Markdown' and position == 1:
            position = 0  # Exit long
            print(f"Sell on {df.index[i]}, Price: {df['close'].iloc[i]}")
            balance += df['close'].iloc[i]

        elif current_phase == 'Accumulation' and position == 0:
            print(f"Watch for breakout during Accumulation on {df.index[i]}")

        elif current_phase == 'Distribution' and position == 1:
            position = 0  # Exit long
            print(f"Sell during Distribution on {df.index[i]}, Price: {df['close'].iloc[i]}")
            balance += df['close'].iloc[i]

    return balance


# Main program
if __name__ == "__main__":
    initialize_mt5()
    # Get historical forex data (EUR/USD in this case)
    pair = "EURUSD"  # EUR/USD currency pair on Yahoo Finance
    forex_data = get_forex_data(pair)

    # Identify market phases using the Wyckoff Method
    forex_data_with_phases = identify_market_phases(forex_data)

    # Simulate trading based on Wyckoff phases
    final_balance = trade_with_wyckoff(forex_data_with_phases)

    print(f"Final balance: {final_balance}")
