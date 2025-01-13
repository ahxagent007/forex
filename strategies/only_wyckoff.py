def detect_accumulation_and_markup(
        data,
        base_accumulation=0.0005,
        acc_multiplier=1,
        base_markup=0.0008,
        markup_multiplier=2.0,
        base_distribution=0.0001,
        dist_multiplier=2,
        base_markdown=0.0008,
        markdown_multiplier=2,
        debug=False
):
    """
    Detect accumulation and markup phases using dynamic thresholds.

    Args:
        data (pd.DataFrame): A DataFrame containing 'close', 'high', 'low', and 'volume'.
        base_accumulation (float): Base threshold for accumulation detection.
        acc_multiplier (float): Multiplier for dynamic accumulation threshold adjustment.
        base_markup (float): Base threshold for markup detection.
        markup_multiplier (float): Multiplier for dynamic markup threshold adjustment.
        debug (bool): If True, print debug information.

    Returns:
        pd.DataFrame: Original data with additional 'accumulation' and 'markup' columns.
    """

    # Calculate rolling mean and standard deviation
    data['mean_price'] = data['close'].rolling(100, min_periods=1).mean()
    data['std_dev'] = data['close'].rolling(100, min_periods=1).std()

    # Calculate ATR for volatility-based thresholds
    data['high_low'] = data['high'] - data['low']
    data['high_close'] = abs(data['high'] - data['close'].shift(1))
    data['low_close'] = abs(data['low'] - data['close'].shift(1))
    data['true_range'] = data[['high_low', 'high_close', 'low_close']].max(axis=1)
    data['atr'] = data['true_range'].rolling(window=21, min_periods=1).mean()

    # Dynamic accumulation threshold
    data['dynamic_accumulation_threshold'] = (
            base_accumulation + acc_multiplier * (data['atr'] / data['close'].mean())
    )
    data['price_dev'] = abs(data['close'] - data['mean_price']) / data['mean_price']
    data['accumulation'] = data['price_dev'] <= data['dynamic_accumulation_threshold']

    # Dynamic markup threshold based on returns volatility
    data['returns'] = data['close'].pct_change()
    data['returns_std'] = data['returns'].rolling(window=100, min_periods=1).std()
    data['dynamic_markup_threshold'] = base_markup + markup_multiplier * data['returns_std']
    data['markup'] = data['returns'] >= data['dynamic_markup_threshold']

    data['dynamic_distribution_threshold'] = (
            base_distribution + dist_multiplier * (data['atr'] / data['close'].mean())
    )
    data['price_dev'] = abs(data['close'] - data['mean_price']) / data['mean_price']
    data['distribution'] = data['price_dev'] <= data['dynamic_distribution_threshold']

    # Dynamic markdown threshold based on returns volatility
    data['returns'] = data['close'].pct_change()
    data['returns_std'] = data['returns'].rolling(window=100, min_periods=1).std()
    data['dynamic_markdown_threshold'] = base_markdown + markdown_multiplier * data['returns_std']
    data['markdown'] = data['returns'] <= -data['dynamic_markdown_threshold']

    data['buy_signal'] = data['accumulation'] & data['markup']
    data['sell_signal'] = data['distribution'] | data['markdown']

    if debug:
        print(data[[
            'close', 'mean_price', 'std_dev', 'atr',
            'dynamic_accumulation_threshold', 'price_dev',
            'dynamic_markup_threshold', 'returns', 'accumulation', 'markup'
        ]])

    return data['accumulation'][-1]