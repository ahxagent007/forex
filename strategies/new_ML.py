import time
import datetime as dt
from mt5_utils import get_live_data, trade_order_price, calculate_lot_size, initialize_mt5, trade_order_wo_tp_sl, \
    close_all_positions, get_open_positions, get_all_positions
from common_functions import check_duplicate_orders_time, check_duplicate_orders_magic, check_duplicate_orders, \
    write_json, check_duplicate_orders_is_time, isNowInTimePeriod, price_distance_percent


mt5 = initialize_mt5()

SYMBOL_LIST = ['GBPUSD', 'USDCHF', 'USDJPY', 'US30', 'EURGBP', 'AUDUSD', 'XAUUSD', 'EURUSD']


# ========================== CONFIG ==========================
SYMBOL        = "EURUSD"
TIMEFRAME     = "M5"          # M1, M5, M15, M30, H1, H4, D1
NUM_BARS      = 20000         # more is better
UTC_SHIFT_MIN = 0             # if you want to shift time index

# Labeling
HORIZON       = 6             # predict next N bars outcome (e.g., next 6 x M5 = 30 min)
THRESH_BPS    = 3             # threshold in basis points (0.01% = 1 bp). 3 bps ≈ 0.0003 for majors

# Backtest
SPREAD_PIPS   = 0.8           # average spread (pips)
COMMISSION_PER_TRADE = 0.0    # if your broker charges fixed commission
MAX_POS_BARS  = HORIZON       # close position after this many bars if TP/SL not hit (simple)

# Risk (for live order example)
RISK_PCT      = 0.005         # 0.5% risk per trade
SL_PIPS       = 15            # example stop
TP_PIPS       = 25            # example take profit

# ============================================================

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from math import isnan

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ---------------------- Helpers ----------------------
TF_MAP = {
    "M1": mt5.TIMEFRAME_M1, "M2": mt5.TIMEFRAME_M2, "M3": mt5.TIMEFRAME_M3,
    "M4": mt5.TIMEFRAME_M4, "M5": mt5.TIMEFRAME_M5, "M6": mt5.TIMEFRAME_M6,
    "M10": mt5.TIMEFRAME_M10, "M12": mt5.TIMEFRAME_M12, "M15": mt5.TIMEFRAME_M15,
    "M20": mt5.TIMEFRAME_M20, "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1,
    "H2": mt5.TIMEFRAME_H2, "H3": mt5.TIMEFRAME_H3, "H4": mt5.TIMEFRAME_H4,
    "H6": mt5.TIMEFRAME_H6, "H8": mt5.TIMEFRAME_H8, "H12": mt5.TIMEFRAME_H12,
    "D1": mt5.TIMEFRAME_D1, "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1
}

def to_utc(ts):
    return datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)

def pips(symbol, points):
    """Convert points to pips for a symbol using its digits."""
    info = mt5.symbol_info(symbol)
    if not info:
        return None
    pip = 0.0001
    if "JPY" in symbol or info.digits == 3:
        pip = 0.01
    elif info.digits == 5 or info.digits == 4:
        pip = 0.0001
    elif info.digits == 2:
        pip = 0.01
    return points / pip

def points_from_pips(symbol, pips_val):
    info = mt5.symbol_info(symbol)
    if not info:
        return None
    pip = 0.0001
    if "JPY" in symbol or info.digits == 3 or info.digits == 2:
        pip = 0.01
    return pips_val * pip

# ---------------------- Indicators ----------------------
def ema(a: pd.Series, span: int) -> pd.Series:
    return a.ewm(span=span, adjust=False).mean()

def rsi(close: pd.Series, period=14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    roll_up = up.ewm(alpha=1/period, adjust=False).mean()
    roll_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = roll_up / (roll_down.replace(0, np.nan))
    rsi_ = 100.0 - (100.0 / (1.0 + rs))
    return rsi_.fillna(50)

def true_range(df):
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr

def atr(df, period=14):
    tr = true_range(df)
    return tr.ewm(alpha=1/period, adjust=False).mean()

# ---------------------- Data from MT5 ----------------------
def fetch_mt5(symbol, timeframe, bars):
    if not mt5.initialize():
        raise RuntimeError("MT5 init failed")
    tf = TF_MAP[timeframe]
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    if rates is None:
        mt5.shutdown()
        raise RuntimeError("copy_rates_from_pos returned None")
    df = pd.DataFrame(rates)
    mt5.shutdown()

    # to UTC datetime index
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    if UTC_SHIFT_MIN != 0:
        df["time"] = df["time"] + pd.Timedelta(minutes=UTC_SHIFT_MIN)
    df.set_index("time", inplace=True)
    df.rename(columns={"tick_volume": "volume"}, inplace=True)
    return df[["open","high","low","close","volume"]]

# ---------------------- Features/Labels ----------------------
def make_features(df: pd.DataFrame) -> pd.DataFrame:
    f = pd.DataFrame(index=df.index)
    f["ret_1"]     = df["close"].pct_change(1)
    f["ret_3"]     = df["close"].pct_change(3)
    f["ret_6"]     = df["close"].pct_change(6)
    f["ema_20"]    = ema(df["close"], 20)
    f["ema_50"]    = ema(df["close"], 50)
    f["ema_200"]   = ema(df["close"], 200)
    f["ema_gap_20"]= (df["close"] - f["ema_20"]) / df["close"]
    f["ema_gap_50"]= (df["close"] - f["ema_50"]) / df["close"]
    f["rsi_14"]    = rsi(df["close"], 14) / 100.0
    f["atr_14"]    = atr(df, 14) / df["close"]  # normalized ATR
    f["hl_range"]  = (df["high"] - df["low"]) / df["close"]
    f["spread_proxy"] = (df["close"] - df["open"]).abs() / df["close"]
    return f.replace([np.inf, -np.inf], np.nan).dropna()

def make_labels(df: pd.DataFrame, horizon=HORIZON, thresh_bps=THRESH_BPS):
    """
    1 -> BUY signal (future return > +threshold)
    -1 -> SELL signal (future return < -threshold)
     0 -> HOLD otherwise
    """
    future_ret = df["close"].shift(-horizon) / df["close"] - 1.0
    up =  thresh_bps * 1e-4
    dn = -thresh_bps * 1e-4
    y = future_ret.copy()
    y[:] = 0
    y[future_ret > up]  =  1
    y[future_ret < dn]  = -1
    return y.loc[~future_ret.isna()]

# ---------------------- Training & CV ----------------------
def time_series_cv_train(X, y, n_splits=5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    model = Pipeline(steps=[
        ("scale", StandardScaler(with_mean=False)),  # tree model tolerates raw; kept for robustness
        ("clf", HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_depth=None,
            max_iter=300,
            l2_regularization=0.0,
            random_state=42))
    ])

    fold_reports = []
    last_train_model = None

    for i, (tr, va) in enumerate(tscv.split(X)):
        Xtr, Xva = X.iloc[tr], X.iloc[va]
        ytr, yva = y.iloc[tr], y.iloc[va]
        model.fit(Xtr, ytr)
        yhat = model.predict(Xva)
        print(f"\n=== Fold {i+1} Report ===")
        print(classification_report(yva, yhat, digits=3))
        print("Confusion matrix:\n", confusion_matrix(yva, yhat, labels=[-1,0,1]))
        fold_reports.append((yva, yhat))
        last_train_model = model

    return last_train_model, fold_reports

# ---------------------- Simple Costed Backtest ----------------------
def simple_backtest(signals: pd.Series, prices: pd.Series, spread_pips=SPREAD_PIPS):
    """
    Enter at bar close on signal; exit after MAX_POS_BARS or opposite signal.
    Cost = spread + commission (simplified).
    """
    # pip conversion
    info = mt5.symbol_info(SYMBOL)
    pip_points = points_from_pips(SYMBOL, 1.0) if info else 0.0001
    spread_points = points_from_pips(SYMBOL, spread_pips) if info else spread_pips*0.0001

    pnl = []
    pos = 0     # -1 short, +1 long, 0 flat
    entry_price = None
    bars_in_pos = 0

    for t in range(len(signals)):
        sig = signals.iloc[t]
        px  = prices.iloc[t]

        if pos == 0 and sig != 0:
            # open
            pos = int(sig)
            entry_price = px
            bars_in_pos = 0
            # pay spread on entry
            entry_cost = (spread_points or 0.0000)
            entry_price = entry_price + entry_cost if pos > 0 else entry_price - entry_cost
        elif pos != 0:
            bars_in_pos += 1
            # exit conditions
            exit_now = False
            if sig == -pos:              # opposite signal
                exit_now = True
            if bars_in_pos >= MAX_POS_BARS:
                exit_now = True
            if exit_now:
                # exit at price + spread
                exit_price = px
                exit_cost  = (spread_points or 0.0000)
                exit_price = exit_price - exit_cost if pos > 0 else exit_price + exit_cost
                trade_ret = (exit_price / entry_price - 1.0) * pos
                # subtract commission as simple fixed amount in price-return terms is negligible here
                pnl.append(trade_ret)
                pos = 0
                entry_price = None
                bars_in_pos = 0

    if pos != 0 and entry_price is not None:
        # force close last
        px = prices.iloc[-1]
        exit_price = px
        exit_cost  = (spread_points or 0.0000)
        exit_price = exit_price - exit_cost if pos > 0 else exit_price + exit_cost
        trade_ret = (exit_price / entry_price - 1.0) * pos
        pnl.append(trade_ret)

    pnl = np.array(pnl) if pnl else np.array([0.0])
    equity = (1.0 + pnl).cumprod()
    print(f"\nBacktest trades: {len(pnl)} | Mean trade ret: {pnl.mean():.5f} | Win%: {(pnl>0).mean():.2%}")
    print(f"Equity (normalized) final: {equity[-1]:.3f}")
    return pnl, equity

# ---------------------- Live Signal → Order (example) ----------------------
def send_order_example(symbol, signal, sl_pips=SL_PIPS, tp_pips=TP_PIPS, risk_pct=RISK_PCT):
    """
    Example only: market order with fixed SL/TP distances.
    """
    if not mt5.initialize():
        print("MT5 init failed for order send")
        return
    info = mt5.symbol_info(symbol)
    if info is None or not info.visible:
        mt5.symbol_select(symbol, True)

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print("No tick info")
        mt5.shutdown()
        return

    price = tick.ask if signal == 1 else tick.bid
    sl_points = points_from_pips(symbol, sl_pips)
    tp_points = points_from_pips(symbol, tp_pips)

    # Lot sizing by risk: approximate pip value
    # For simplicity we assume $10/pip per 1 lot for most FX majors;
    # adjust for your symbol if needed.
    account_info = mt5.account_info()
    balance = account_info.balance if account_info else 1000
    dollar_risk = balance * risk_pct
    pip_value_per_lot = 10.0  # rough for many majors; customize!
    lot = max(0.01, round(dollar_risk / (sl_pips * pip_value_per_lot), 2))

    sl = price - sl_points if signal == 1 else price + sl_points
    tp = price + tp_points if signal == 1 else price - tp_points

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if signal == 1 else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 20250826,
        "comment": "ML-signal",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    result = mt5.order_send(request)
    if result is None:
        print("order_send returned None")
    else:
        print("Order result:", result.retcode, result.comment)
    mt5.shutdown()

# ====================== RUN PIPELINE ======================
if __name__ == "__main__":
    # 1) Load data
    df = fetch_mt5(SYMBOL, TIMEFRAME, NUM_BARS)
    # 2) Build features & align with labels
    feats = make_features(df)
    labels = make_labels(df, HORIZON, THRESH_BPS)
    # Align indexes (drop tail where label NA)
    common_idx = feats.index.intersection(labels.index)
    X = feats.loc[common_idx]
    y = labels.loc[common_idx]

    # 3) Train (time-series CV)
    model, _ = time_series_cv_train(X, y, n_splits=5)

    # 4) Backtest (very simple, signal = model.predict)
    yhat = pd.Series(model.predict(X), index=X.index).astype(int)
    pnl, eq = simple_backtest(yhat, df.loc[yhat.index, "close"], spread_pips=SPREAD_PIPS)

    # 5) Latest bar signal & (optional) send order
    latest_x = X.iloc[[-1]]
    latest_signal = int(model.predict(latest_x)[0])   # -1 / 0 / 1
    print(f"\nLatest signal for {SYMBOL} @ {latest_x.index[-1]}: {latest_signal}  (-1 SELL, 0 HOLD, 1 BUY)")

    #Uncomment to place a live order on signal (be careful!)
    if latest_signal != 0:
        send_order_example(SYMBOL, latest_signal, SL_PIPS, TP_PIPS, RISK_PCT)