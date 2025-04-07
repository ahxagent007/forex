import random
import time

from mt5_utils import get_all_positions, trade_order_wo_tp_sl, close_position, initialize_mt5, get_live_data


def get_buy_or_sell(symbol):
    data_df = get_live_data(symbol = symbol, time_frame='M1', prev_n_candles=100)
    data_df['ema'] = data_df['close'].ewm(span=30, adjust=False).mean()

    if data_df['close'].iloc[-1] > data_df['ema'].iloc[-1]:
        return 1
    else:
        return 0

def start_random_sizing():
    initialize_mt5()
    symbol = 'BTCUSD'
    symbol_list = ['BTCUSD']


    while True:
        for symbol in symbol_list:
            delay_sec = 0.1
            time.sleep(delay_sec)

            positions = get_all_positions(symbol)
            position_count = len(positions)

            lot = 0.01
            tp_sl_dollar = 2
            tp = tp_sl_dollar * lot * 100
            sl = tp_sl_dollar * lot * 100
            break_even = 1 * lot * 100

            if position_count == 0:
                # BUY OR SELL
                #buy_or_sell = random.randint(1, 2)
                buy_or_sell = get_buy_or_sell(symbol)
                if buy_or_sell == 1:
                    trade_order_wo_tp_sl(symbol=symbol, lot=lot, action='buy', magic=True)
                else:
                    trade_order_wo_tp_sl(symbol=symbol, lot=lot, action='sell', magic=True)


            elif position_count == 1:
                if positions[0].profit > tp:
                    # Close Position
                    close_position(symbol, positions[0].ticket)
                    # Buy or Sell Randomly
                    #buy_or_sell = random.randint(1, 2)
                    buy_or_sell = get_buy_or_sell(symbol)
                    if buy_or_sell == 1:
                        trade_order_wo_tp_sl(symbol=symbol, lot=lot, action='buy', magic=True)
                    else:
                        trade_order_wo_tp_sl(symbol=symbol, lot=lot, action='sell', magic=True)
                elif positions[0].profit < -sl:
                    trade_order_wo_tp_sl(symbol=symbol, lot=lot, action=positions[0].comment, magic=True)
            elif position_count > 1:
                profit_sum = 0
                for position in positions:
                    profit_sum += position.profit

                if profit_sum > break_even:
                    # Close all positions
                    for position in positions:
                        close_position(symbol, position.ticket)
                elif profit_sum < (-sl * position_count):
                    if position_count > 4:
                        continue
                    # Same trade
                    prev_action = position.comment
                    trade_order_wo_tp_sl(symbol=symbol, lot=lot, action=prev_action, magic=True)

                #print('Profit', symbol, profit_sum)

start_random_sizing()