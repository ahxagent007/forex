from mt5_utils import get_live_data, get_prev_data, initialize_mt5
import plotly.graph_objects as go
import matplotlib.pyplot as plt


def create_candle_type(df):
    df['candle_type'] = None

    for idx, row in df.iterrows():
        high = row['high']
        low = row['low']
        open = row['open']
        close = row['close']

        #AVG
        diff_array = []
        for i in range(1, 6):
            try:
                diff = abs(df.loc[idx-i, 'open'] - df.loc[idx-1, 'close'])
                diff_array.append(diff)
            except:
                None
        try:
            prev_5_avg_candle_size = sum(diff_array) / len(diff_array)
        except:
            prev_5_avg_candle_size = 0

        length = abs(high - low)

        hc_diff = abs(high - close)
        lo_diff = abs(low - open)

        ho_diff = abs(high - open)
        lc_diff = abs(low - close)

        oc_diff = abs(open-close)

        ## Bullish Marubozu
        if (hc_diff/length)*100 < 5 and (lo_diff/length)*100 < 5 and close>open and oc_diff > prev_5_avg_candle_size:
            df.loc[idx, 'candle_type'] = 'bullish_marubozu'

        ## bearish Marubozu
        elif (ho_diff/length)*100 < 5 and (lc_diff/length)*100 < 5 and open>close and oc_diff > prev_5_avg_candle_size:
            df.loc[idx, 'candle_type'] = 'bearish_marubozu'

        ## Hammer
        elif (oc_diff/length)*100 < 10 and (hc_diff/length)*100 < 15 and lo_diff > oc_diff*2 and close>open:
            df.loc[idx, 'candle_type'] = 'bullish_hammer'

        ## Hanging Man
        elif (oc_diff/length)*100 < 10 and (ho_diff/length)*100 < 15 and lc_diff > oc_diff*2 and open>close:
            df.loc[idx, 'candle_type'] = 'bearish_hanging_man'

        ## inverted Hammer
        elif (oc_diff/length)*100 < 10 and (lo_diff/length)*100 < 15 and hc_diff > oc_diff*2 and close>open:
            df.loc[idx, 'candle_type'] = 'bullish_inverted_hammer'

        ## Shooting Star
        elif (oc_diff/length)*100 < 10 and (lc_diff/length)*100 < 15 and ho_diff > oc_diff*2 and open>close:
            df.loc[idx, 'candle_type'] = 'bearish_shooting_star'

        ## Doji
        elif (oc_diff/length)*100 < 5:
            df.loc[idx, 'candle_type'] = 'doji'

    return df

def plot_data(df):
    fig = go.Figure(data=[go.Candlestick(x=df['time'],
                                         open=df['open'], high=df['high'],
                                         low=df['low'], close=df['close'])
                          ])

    for idx, row in df.iterrows():
        if row['candle_type']:
            fig.add_annotation(x=row['time'], y=row['low']-0.0005, text=row['candle_type'], showarrow=False,
                               font=dict(size=12, color='black'), textangle=90)
    #fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()

def plot_line(df):
    # plotting a line graph
    print("Line graph: ")
    plt.plot(df["time"][:50], df["close"][:50])
    plt.savefig('image.jpg')
    plt.show()



def test_xian():

    initialize_mt5()

    symbol = 'XAUUSD'
    time_frame = 'H4'
    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=400)

    df = create_candle_type(df)

    plot_line(df)

test_xian()


