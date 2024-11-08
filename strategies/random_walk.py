import random

import pandas as pd


def create_random_path(n=10):
    action_list = []

    for i in range(n):
        action = random.randrange(1,3)

        if action == 1:
            action_list.append('buy')
        else:
            action_list.append('sell')

    print(action_list)

def get_random_action():
    action = random.randrange(1, 3)

    if action == 1:
        return 'buy'
    else:
        return 'sell'


def backtest_random_walk(data):
    win_count = 0
    lose_count = 0
    win_amount = 0
    lose_amount = 0

    i_list = []
    i = 0
    while i < data.shape[0] - 1:
        i_list.append(i)
        action = get_random_action()

        amount = data['close'].iloc[i] - data['open'].iloc[i]
        if action == 'buy':
            if amount > 0:
                win_amount += amount
                while True:
                    i += 1
                    if data['close'].iloc[i] > data['open'].iloc[i]:
                        amount = data['close'].iloc[i] - data['open'].iloc[i]
                        win_amount += amount
                    else:
                        break
                win_count += 1

            else:
                lose_count += 1
                lose_amount += abs(amount)
                i += 1
        elif action == 'sell':
            if amount < 0:
                win_amount += abs(amount)
                while True:
                    i += 1
                    if data['close'].iloc[i] < data['open'].iloc[i]:
                        amount = abs(data['close'].iloc[i] - data['open'].iloc[i])
                        win_amount += amount
                    else:
                        break
                win_count += 1
            else:
                lose_count += 1
                lose_amount += amount
                i += 1

    win_amount *= 100000
    lose_amount *= 100000

    print('TOTAL TRADE: ', len(i_list))
    print('COUNT: WIN =', win_count, ' LOSE =', lose_count)
    print('WIN AMOUNT: ', win_amount)
    print('LOSE AMOUNT: ', lose_amount)
    print('GAIN: ', (win_amount - lose_amount) - (win_count * 6))


def multiple_backtest():
    data = pd.read_csv('eurusd_1m.csv')

    for i in range(0, 10):
        print('RANDOM CASE ', i + 1)
        backtest_random_walk(data)
        print('--------------------------------')

