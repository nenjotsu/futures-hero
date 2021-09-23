import pandas as pd

def compute(length, dataset):
    df = pd.DataFrame(dataset)
    ema = df.ewm(span=length).mean()
    return ema[0].values.tolist()

def cal_rsi(dataset):
    periods = 14
    close_delta = pd.DataFrame(dataset).diff()

    # Make two series: one for lower closes and one for higher closes
    up = close_delta.clip(upper=0)
    down = -1 * close_delta.clip(lower=0)
    
    ma_up = up.ewm(com = periods, adjust=True, min_periods = periods).mean()
    ma_down = down.ewm(com = periods, adjust=True, min_periods = periods).mean()

    rs = ma_up / ma_down
    rsi = 100 - (100/(1 + rs))
    return rsi[0].values.tolist()

def current_RSI(dataset):
    return round(float(cal_rsi(dataset)[-1]), 2)
