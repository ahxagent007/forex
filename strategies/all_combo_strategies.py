from combo.boillinger_macd_combo import boil_macd
from combo.fibonacci_price_action_combo import fibonacci_price_action
from combo.ichimoku_cloud_stochastic_oscillator_combo import ichimoku_stochastic
from combo.mac_rsi_combo import mac_rsi
from ..mt5_utils import trade_order

def combo_strategies(symbol):

    all_actions = []

    bol_macd_signal = boil_macd(symbol)
    if bol_macd_signal:
        print('bol_macd_signal', bol_macd_signal)
        all_actions.append(bol_macd_signal)

    fibonacci_price_signal = fibonacci_price_action(symbol)
    if fibonacci_price_signal:
        print('fibonacci_price_signal', fibonacci_price_signal)
        all_actions.append(fibonacci_price_signal)

    ichimoku_stochastic_signal = ichimoku_stochastic()
    if ichimoku_stochastic_signal:
        print('ichimoku_stochastic_signal', ichimoku_stochastic_signal)
        all_actions.append(ichimoku_stochastic_signal)

    mac_rsi_signal = mac_rsi(symbol)
    if mac_rsi_signal:
        print('mac_rsi_signal', mac_rsi_signal)
        all_actions.append(mac_rsi_signal)

    buy_signals = 0
    sell_signals = 0

    for signal in all_actions:
        if signal == 'buy':
            buy_signals += 1
        elif signal == 'sell':
            sell_signals += 1

    tp_point = 100
    sl_point = 50
    lot = 0.01

    if buy_signals > sell_signals:
        action = 'buy'
        trade_order(symbol, tp_point, sl_point, lot, action)
    elif sell_signals > buy_signals:
        action = 'sell'
        trade_order(symbol, tp_point, sl_point, lot, action)


