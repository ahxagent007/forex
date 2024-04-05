

def three_white_soliders(current, prev, b_prev, b1_prev, b2_prev):

    #check downtrend
    if (b1_prev['open'] > b1_prev['close']) and (b2_prev['open'] > b2_prev['close']):
        NotImplemented



current = {
    'open': 3.0,
    'close': 3.1,
    'high': 4.2,
    'low': 2.0
}

prev = {
    'open': 3.0,
    'close': 3.1,
    'high': 4.2,
    'low': 2.0
}

b_prev = {
    'open': 3.0,
    'close': 3.1,
    'high': 4.2,
    'low': 2.0
}