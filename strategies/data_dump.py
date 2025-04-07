from mt5_utils import initialize_mt5, get_live_data

initialize_mt5()

symbol = 'EURUSD'
df = get_live_data(symbol=symbol, time_frame='M5', prev_n_candles=90000)
print(df.shape)

df.to_csv(symbol+'.csv')