import RSI
import config
import candlestick
import get_position
import heikin_ashi
import hybrid
import binance_futures_api
import numpy as np
from datetime import datetime, timedelta
from termcolor import colored

def lets_make_some_money(i):
    response = binance_futures_api.position_information(i)
    klines_4h = binance_futures_api.KLINE_INTERVAL_4HOUR(i)
    klines_1h = binance_futures_api.KLINE_INTERVAL_1HOUR(i)
    klines_5m  = binance_futures_api.KLINE_INTERVAL_5MINUTE(i)
    klines_1m  = binance_futures_api.KLINE_INTERVAL_1MINUTE(i)
    position_info = get_position.get_position_info(i, response)
    profit_threshold = get_position.profit_threshold()

    rsi_5m = RSI.current_RSI(candlestick.closing_price_list(klines_5m))
    rsi_1m = RSI.current_RSI(candlestick.closing_price_list(klines_1m))

    candlestick.output(klines_4h)
    candlestick.output(klines_1h)
    candlestick.output(klines_5m)
    candlestick.output(klines_1m)
    print()
    heikin_ashi.output(klines_4h)
    heikin_ashi.output(klines_1h)
    heikin_ashi.output(klines_5m)
    heikin_ashi.output(klines_1m)

    leverage = config.leverage[i]
    if int(response.get("leverage")) != leverage: binance_futures_api.change_leverage(i, leverage)
    if response.get('marginType') != "isolated": binance_futures_api.change_margin_to_ISOLATED(i)

    if position_info == "LONGING":
        if EXIT_LONG(response, profit_threshold, klines_1m): binance_futures_api.close_position(i, "LONG")
        else: print(colored("ACTION           :   HOLDING_LONG", "green"))

    elif position_info == "SHORTING":
        if EXIT_SHORT(response, profit_threshold, klines_1m): binance_futures_api.close_position(i, "SHORT")
        else: print(colored("ACTION           :   HOLDING_SHORT", "red"))

    else:
        if GO_LONG(klines_4h, klines_1h, klines_5m, klines_1m, rsi_5m, rsi_1m): binance_futures_api.open_position(i, "LONG", config.quantity[i])
        elif GO_SHORT(klines_4h, klines_1h, klines_5m, klines_1m, rsi_5m, rsi_1m): binance_futures_api.open_position(i, "SHORT", config.quantity[i])
        else: print("ACTION           :   🐺 WAIT 🐺")

    print("Last action executed @ " + datetime.now().strftime("%H:%M:%S") + "\n")
    if not config.live_trade: print_entry_condition(klines_4h, klines_1h, klines_5m, klines_1m, rsi_5m, rsi_1m)

def hot_zone(klines_30m, klines_1h):
    if klines_1h[-1][0] == klines_30m[-1][0]: return True

def GO_LONG(klines_4h, klines_1h, klines_5m, klines_1m, rsi_5m, rsi_1m):
    if  hybrid.strong_trend(klines_4h) == "GREEN" and \
        hybrid.strong_trend(klines_1h) == "GREEN" and \
        heikin_ashi.VALID_CANDLE(klines_5m) == "GREEN" and \
        heikin_ashi.VALID_CANDLE(klines_1m) == "GREEN" and \
        rsi_5m < 70 and rsi_1m < 70: return True

def GO_SHORT(klines_4h, klines_1h, klines_5m, klines_1m, rsi_5m, rsi_1m):
    if  hybrid.strong_trend(klines_4h) == "RED" and \
        hybrid.strong_trend(klines_1h) == "RED" and \
        heikin_ashi.VALID_CANDLE(klines_5m) == "RED" and \
        heikin_ashi.VALID_CANDLE(klines_1m) == "RED" and \
        rsi_5m > 30 and rsi_1m > 30: return True

def EXIT_LONG(response, profit_threshold, klines_1m):
    if get_position.profit_or_loss(response, profit_threshold) == "PROFIT":
        if heikin_ashi.VALID_CANDLE(klines_1m) == "RED": return True

def EXIT_SHORT(response, profit_threshold, klines_1m):
    if get_position.profit_or_loss(response, profit_threshold) == "PROFIT":
        if heikin_ashi.VALID_CANDLE(klines_1m) == "GREEN": return True

def print_entry_condition(klines_4h, klines_1h, klines_5m, klines_1m, rsi_5m, rsi_1m):
    test_color = "RED".upper()
    print("4 HOUR YES") if hybrid.strong_trend(klines_4h) == test_color else print("4 HOUR NO")
    print("1 HOUR YES") if hybrid.strong_trend(klines_1h) == test_color else print("1 HOUR NO")
    print("5 MIN  YES") if heikin_ashi.VALID_CANDLE(klines_5m) == test_color else print("5 MIN  NO")
    print("1 MIN  YES") if heikin_ashi.VALID_CANDLE(klines_1m) == test_color else print("1 MIN  NO")
    print("5MIN RSI " + str(rsi_5m))
    print("1MIN RSI " + str(rsi_1m))
    print()
