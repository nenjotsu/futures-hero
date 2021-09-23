import pandas as pd
import qtpylib
import config
# import talib.abstract as ta
import pandas_ta as ta
from talib import abstract

def binanceDataFrame(klines):
    df = pd.DataFrame(klines.reshape(-1,12),dtype=float, columns = ('open time',
                                                                    'open',
                                                                    'high',
                                                                    'low',
                                                                    'close',
                                                                    'volume',
                                                                    'close time',
                                                                    'quote asset volume',
                                                                    'number of trades',
                                                                    'taker buy base asset volume',
                                                                    'taker buy quote asset volume',
                                                                    'ignore'))

    df['open time'] = pd.to_datetime(df['open time'], unit='ms')


    return df

def get_ema_uptrend(dataset):
    df = binanceDataFrame(dataset)
    df['emaShort'] = ta.ema(df["close"], length=config.ema_short)
    df['emaLong'] = ta.ema(df["close"], length=config.ema_long)
    short = df['emaShort']
    long = df['emaLong']
    is_short_gt_long = (short.shift(2) > long.shift(1))
    df['is_uptrend'] = (short.shift(3) < short.shift(1))
    return df[df['is_uptrend'].notna()].tail(1)

def get_ema_uptrend_next(dataset):
    df = binanceDataFrame(dataset)
    df['emaShort'] = ta.ema(df["close"], length=config.ema_short)
    df['emaLong'] = ta.ema(df["close"], length=config.ema_long)
    short = df['emaShort']
    long = df['emaLong']
    # is_short_gt_long = (short.shift(1) > long.shift(1))
    df['is_uptrend'] = (short.shift(2) < short.shift(1))
    return df[df['is_uptrend'].notna()].tail(1)
    
def get_ema_downtrend(dataset):
    df = binanceDataFrame(dataset)
    df['emaShort'] = ta.ema(df["close"], length=config.ema_short)
    df['emaLong'] = ta.ema(df["close"], length=config.ema_long)
    short = df['emaShort']
    long = df['emaLong']
    is_short_lt_long = (short.shift(1) < long.shift(1))
    # df['is_downtrend'] = (is_short_lt_long & (short.shift(3) > short.shift(1)))
    df['is_downtrend'] = (short.shift(3) > short.shift(1))
    return df[df['is_downtrend'].notna()].tail(1)
    
def get_ema_downtrend_next(dataset):
    df = binanceDataFrame(dataset)
    df['emaShort'] = ta.ema(df["close"], length=config.ema_short)
    df['emaLong'] = ta.ema(df["close"], length=config.ema_long)
    short = df['emaShort']
    long = df['emaLong']
    # is_short_lt_long = (short.shift(1) < long.shift(1))
    df['is_downtrend'] = (short.shift(2) > short.shift(1))
    return df[df['is_downtrend'].notna()].tail(1)

def get_bb(dataset):
    df = binanceDataFrame(dataset)
    bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(df), window=20, stds=2)
    df['bb_lowerband'] = bollinger['lower']
    df['bb_middleband'] = bollinger['mid']
    df['bb_upperband'] = bollinger['upper']
    df["bb_percent"] = (
        (df["close"] - df["bb_lowerband"]) /
        (df["bb_upperband"] - df["bb_lowerband"])
    )
    
    return df.tail(1)

def get_bb_middle_uptrend(dataset):
    df = binanceDataFrame(dataset)
    bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(df), window=20, stds=2)
    df['bb_lowerband'] = bollinger['lower']
    df['bb_middleband'] = bollinger['mid']
    df['bb_upperband'] = bollinger['upper']
    df["bb_percent"] = (
        (df["close"] - df["bb_lowerband"]) /
        (df["bb_upperband"] - df["bb_lowerband"])
    )
    df['bb_middle_uptrend'] = (df['bb_middleband'].shift(2) < df['bb_middleband'].shift(1))
    return df[df['bb_middle_uptrend'].notna()].tail(1)

def get_bb_middle_downtrend(dataset):
    df = binanceDataFrame(dataset)
    bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(df), window=20, stds=2)
    df['bb_lowerband'] = bollinger['lower']
    df['bb_middleband'] = bollinger['mid']
    df['bb_upperband'] = bollinger['upper']
    df["bb_percent"] = (
        (df["close"] - df["bb_lowerband"]) /
        (df["bb_upperband"] - df["bb_lowerband"])
    )
    df['bb_middle_downtrend'] = (df['bb_middleband'].shift(2) > df['bb_middleband'].shift(1))
    return df[df['bb_middle_downtrend'].notna()].tail(1)

# def is_above(value, target):
#     return (value < target) & (value.shift(1) < target)


def get_bb_percent(dataset):
    df = binanceDataFrame(dataset)
    bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(df), window=20, stds=2)
    df['bb_lowerband'] = bollinger['lower']
    df['bb_middleband'] = bollinger['mid']
    df['bb_upperband'] = bollinger['upper']
    df["bb_percent"] = (
        (df["close"] - df["bb_lowerband"]) /
        (df["bb_upperband"] - df["bb_lowerband"])
    )
    # df[] = df[df['bb_percent'].notna()].iloc[-1]
    # print('bb_percent', bb_percent['bb_percent'])

    is_cross_above = qtpylib.crossed_above(df['bb_percent'], config.bb_buy)
    is_cross_below = qtpylib.crossed_below(df['bb_percent'], config.bb_sell)

    return is_cross_above.iloc[-1], is_cross_below.iloc[-1]

def get_rsi(dataset):
    df = binanceDataFrame(dataset)
    df['rsi'] = abstract.RSI(df['close'], timeperiod=14)
    rsi = {}
    rsi['prev'] = df[df['rsi'].notna()].iloc[-2]
    rsi['curr'] = df[df['rsi'].notna()].iloc[-1]

    label = "RSI_IDLE"

    if (config.rsi_buy > rsi['prev']['rsi']) & (rsi['prev']['rsi'] < rsi['curr']['rsi']) & (config.rsi_buy < rsi['curr']['rsi']):
        label = "RSI_LONG"
    if (config.rsi_sell < rsi['prev']['rsi']) & (rsi['prev']['rsi'] > rsi['curr']['rsi']) & (config.rsi_sell > rsi['curr']['rsi']):
        label = "RSI_SHORT"
    # , rsi['prev']['rsi'], rsi['curr']['rsi']
    return label

def get_mfi_crossed_above(dataset):
    df = binanceDataFrame(dataset)
    df['mfi'] = abstract.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=11)
    mfi = df[df['mfi'].notna()].iloc[-1]
    # mfi_prev = round(float(df['mfi'].shift(1).iat[-1]), 1)
    # print('mfi_prev', mfi_prev)
    # mfi_curr = round(float(df['mfi'].iat[-1]), 1)
    # print('mfi_curr', mfi['mfi'])
    return mfi['mfi']
    # print('mfi', mfi)
    # return mfi_prev < mfi_curr
    # return qtpylib.crossed_above(dftail['rsi'], config.rsi_buy)

def get_stock_rsi(dataset):
    df = binanceDataFrame(dataset)
    fastk, fastd = abstract.STOCHRSI(df['close'], timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0, fastk_matype=0)

    # print('fastk', fastk)
    df['fastk'] = fastk
    df['fastd'] = fastd
    dffastk = df[df['fastk'].notna()].iloc[-1]
    dffastd = df[df['fastd'].notna()].iloc[-1]
    print('fastk', dffastk['fastk'])
    print('fastd', dffastd['fastd'])
    # stoch_rsi = abstract.STOCHRSI(dataframe)
        # dataframe['fastd_rsi'] = stoch_rsi['fastd']
        # dataframe['fastk_rsi'] = stoch_rsi['fastk']
    