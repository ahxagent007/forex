from common_functions import check_duplicate_orders, write_json #get_sl_tp_pips
from boillinger_macd_combo import boil_macd
from fibonacci_price_action_combo import fibonacci_price_action
from ichimoku_cloud_stochastic_oscillator_combo import ichimoku_stochastic
from mac_rsi_combo import mac_rsi
from mt5_utils import trade_order, get_live_data


def combo_strategies(symbol):
    json_file_name = 'combo_stats'
    running_trade_status, orders_json = check_duplicate_orders(symbol=symbol, skip_min=60,
                                                               json_file_name=json_file_name)
    if running_trade_status:
        print('COMBO  MULTIPLE TRADE >>>', symbol)
        return None

    all_actions = []

    bol_macd_signal = boil_macd(symbol)
    if bol_macd_signal:
        print('bol_macd_signal', bol_macd_signal)
        all_actions.append(bol_macd_signal)

    fibonacci_price_signal = fibonacci_price_action(symbol)
    if fibonacci_price_signal:
        print('fibonacci_price_signal', fibonacci_price_signal)
        all_actions.append(fibonacci_price_signal)

    ichimoku_stochastic_signal = ichimoku_stochastic(symbol)
    if ichimoku_stochastic_signal:
        print('ichimoku_stochastic_signal', ichimoku_stochastic_signal)
        all_actions.append(ichimoku_stochastic_signal)

    mac_rsi_signal = mac_rsi(symbol)
    if mac_rsi_signal:
        print('mac_rsi_signal', mac_rsi_signal)
        all_actions.append(mac_rsi_signal)

    print('COMBO STRATEGIES RESULT >>> ',symbol, all_actions)

    buy_signals = 0
    sell_signals = 0

    for signal in all_actions:
        if signal == 'buy':
            buy_signals += 1
        elif signal == 'sell':
            sell_signals += 1

    # df = get_live_data(symbol=symbol, time_frame='M30', prev_n_candles=20)
    # sl_tp = get_sl_tp_pips(df=df, sl=2, tp=6)
    #
    # tp_point = sl_tp['tp']
    # sl_point = sl_tp['sl']

    tp_point = 100
    sl_point = 300
    lot = 0.01

    if buy_signals > sell_signals:
        action = 'buy'
        trade_order(symbol, tp_point, sl_point, lot, action)
        write_json(json_dict=orders_json, json_file_name=json_file_name)
    elif sell_signals > buy_signals:
        action = 'sell'
        trade_order(symbol, tp_point, sl_point, lot, action)
        write_json(json_dict=orders_json, json_file_name=json_file_name)


