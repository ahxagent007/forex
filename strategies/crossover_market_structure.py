import time

from fx_alex import identify_trend_points, determine_market_trend
from common_functions import check_duplicate_orders_is_time, write_json, check_duplicate_orders
from mt5_utils import get_live_data, get_magic_number, trade_order_magic_value, trade_order_price, initialize_mt5

initialize_mt5()

symbol_list = ['BTCUSD', 'ETHUSD', 'EURUSD', 'AUDUSD', 'GBPUSD', 'NZDUSD', 'EURCHF', 'GBPCHF', 'AUDCHF', 'USDCHF','AUDCAD', 'NZDCAD', 'USDCAD', 'EURCAD',
             'GBPCAD','EURNZD', 'EURGBP', 'EURAUD', 'GBPNZD', 'CADJPY',  'USDJPY', 'EURJPY', 'GBPJPY', 'CHFJPY', 'AUDJPY', 'XAUUSD']
skip_min = 5
time_frame = 'M5'

short = 2
long = 50

while True:
    time.sleep(2)

    for symbol in symbol_list:

        json_file_name = 'xian_ma_cross_structure'
        running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=skip_min,
                                                                                    json_file_name=json_file_name)
        if running_trade_status:
            continue

        df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=300)

        # Moving Average
        df['short'] = df['close'].rolling(window=short).mean()
        df['long'] = df['close'].rolling(window=long).mean()

        action = None
        if df['short'].iloc[-1] > df['long'].iloc[-1] and df['short'].iloc[-3] < df['long'].iloc[-1]:
            action = 'buy'
        elif df['short'].iloc[-1] < df['long'].iloc[-1] and df['short'].iloc[-3] > df['long'].iloc[-1]:
            action = 'sell'

        lot = 0.1

        if action:

            df_high = get_live_data(symbol=symbol, time_frame='H1', prev_n_candles=100)
            df_high = identify_trend_points(df_high)
            market_trend = determine_market_trend(df_high)

            # plot graph
            # plot_bos(result_df)

            # Bullish BOS / Bearish BOS

            if market_trend == 'Bullish':
                # BUY
                market_action = 'buy'
            elif market_trend == 'Bearish':
                # Sell
                market_action = 'sell'
            else:
                market_action = market_trend

            if not market_action == action:
                #print(symbol, 'market_action', market_action, 'action', action)
                continue

            sl = 0
            ## SL TP Calculations
            if action == 'buy':
                # For BUY
                last_min_close = df.tail(5)['close'].min()
                last_min_open = df.tail(5)['open'].min()

                if last_min_close > last_min_open:
                    sl = last_min_close
                else:
                    sl = last_min_open

            elif action == 'sell':
                ## FOR SELL
                last_max_close = df.tail(5)['close'].max()
                last_max_open = df.tail(5)['open'].max()

                if last_max_close > last_max_open:
                    sl = last_max_close
                else:
                    sl = last_max_open

            tp = df['close'].iloc[-1] + (abs(df['close'].iloc[-1] - sl) * 4)

            print(symbol, '## TP -->', tp, '## SL -->', sl, '## ACTION -->', action)

            lot = 0.1
            MAGIC_NUMBER = get_magic_number()

            try:
                trade_order_price(symbol=symbol, tp_price=tp, sl_price=sl, lot=lot, action=action, magic=True,
                                  code=106049,
                                  MAGIC_NUMBER=MAGIC_NUMBER)
                write_json(json_dict=orders_json, json_file_name=json_file_name)
            except Exception as e:
                print(str(e))

