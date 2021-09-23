
import RSI
import indicator
import config
import candlestick
import get_position
import heikin_ashi
import hybrid
import binance_futures_api
import numpy as np
from datetime import datetime, timedelta
from termcolor import colored
import time

sleep_time = 180 # in seconds

def lets_make_some_money(i):
    response = binance_futures_api.position_information(i)
    # klines_4h = binance_futures_api.KLINE_INTERVAL_4HOUR(i)
    klines_2h = binance_futures_api.KLINE_INTERVAL_2HOUR(i)
    klines_1h = binance_futures_api.KLINE_INTERVAL_1HOUR(i)
    klines_30m = binance_futures_api.KLINE_INTERVAL_30MINUTE(i)
    klines_15m = binance_futures_api.KLINE_INTERVAL_15MINUTE(i)
    klines_5m  = binance_futures_api.KLINE_INTERVAL_5MINUTE(i)
    klines_1m  = binance_futures_api.KLINE_INTERVAL_1MINUTE(i)
    position_info = get_position.get_position_info(i, response)
    profit_threshold = get_position.profit_threshold()

    rsi_5m = RSI.current_RSI(candlestick.closing_price_list(klines_5m))
    rsi_1m = RSI.current_RSI(candlestick.closing_price_list(klines_1m))

    rsi_trend_1m = indicator.get_rsi(np.array(klines_1m))
    rsi_trend_5m = indicator.get_rsi(np.array(klines_5m))
    # rsi_1m = int(indicator.get_rsi(np.array(klines_1m))['rsi'].iloc[-1])
    # stock_rsi_5m = indicator.get_stock_rsi(np.array(klines_1m))
    # bb_buy_1m, bb_sell_1m = indicator.get_bb_percent(np.array(klines_1m))

    # print("bb_buy_1m", bb_buy_1m)
    # print("bb_sell_1m", bb_sell_1m)
    # print("mfi_crossed_above_5m", mfi_crossed_above_5m)
    # print("rsi_1m", rsi_1m)

    # round(float(cal_rsi(dataset)[-1]), 2)

    # startDate = datetime.now() - timedelta(days=60)

    # ema_short_5m = indicator.get_ema(np.array(klines_1m))
    # klines1m = np.array(binance_futures_api.client.get_historical_klines(i, '1m', startDate.strftime("%H:%M:%S"), datetime.now().strftime("%H:%M:%S")))

    # print('trend', trend)

    # candlestick.output(klines_4h)
    # candlestick.output(klines_2h)
    candlestick.output(klines_30m)
    candlestick.output(klines_15m)
    # candlestick.output(klines_5m)
    candlestick.output(klines_5m)
    candlestick.output(klines_1m)
    # print()
    heikin_ashi.output(klines_30m)
    heikin_ashi.output(klines_15m)
    heikin_ashi.output(klines_5m)
    heikin_ashi.output(klines_1m)
    is_uptrend_1m = indicator.get_ema_uptrend(np.array(klines_1m))
    is_downtrend_1m = indicator.get_ema_downtrend(np.array(klines_1m))

    is_uptrend_5m = indicator.get_ema_uptrend_next(np.array(klines_5m))
    is_downtrend_5m = indicator.get_ema_downtrend_next(np.array(klines_5m))

    is_uptrend_15m = indicator.get_ema_uptrend_next(np.array(klines_15m))
    is_downtrend_15m = indicator.get_ema_downtrend_next(np.array(klines_15m))

    bb_1m = indicator.get_bb(np.array(klines_1m))
    bb_5m = indicator.get_bb(np.array(klines_5m))
    
    bb_15m_uptrend = indicator.get_bb_middle_uptrend(np.array(klines_15m))
    # print("bb_15m_uptrend", bb_15m_uptrend['bb_middle_uptrend'])

    bb_15m_downtrend = indicator.get_bb_middle_downtrend(np.array(klines_15m))
    # print("bb_15m_downtrend", bb_15m_downtrend['bb_middle_downtrend'])

    side = "WAITING..."

    # ob = binance_futures_api.futures_order_book(i)
    # bid_price = binance_futures_api.truncate(float(ob['bids'][3][0]), config.coin_decimal)
    # ask_price = binance_futures_api.truncate(float(ob['asks'][3][0]), config.coin_decimal)

    leverage = config.leverage[i]
    
    if int(response.get("leverage")) != leverage: binance_futures_api.change_leverage(i, leverage)
    if response.get('marginType') != "isolated": binance_futures_api.change_margin_to_ISOLATED(i)

    if position_info == "LONGING":
        if EXIT_LONG(response, profit_threshold, klines_5m, klines_1m, rsi_5m, i):
            binance_futures_api.close_position(i, "LONG", config.quantity[i])
            time.sleep(sleep_time)
        else: print(colored("ACTION           :   HOLDING_LONG", "green"))

    elif position_info == "SHORTING":
        if EXIT_SHORT(response, profit_threshold, klines_5m, klines_1m, rsi_5m):
            binance_futures_api.close_position(i, "SHORT", config.quantity[i])
            time.sleep(sleep_time)
        else: print(colored("ACTION           :   HOLDING_SHORT", "red"))

    else:
        if GO_LONG(klines_2h, klines_30m, klines_15m, klines_5m, klines_1m, rsi_trend_5m, rsi_5m, rsi_1m, bb_15m_uptrend, bb_15m_downtrend, bb_5m, bb_1m, is_uptrend_1m, is_uptrend_5m, is_uptrend_15m):
            side = "LONG"
            binance_futures_api.open_position(i, "LONG", config.quantity[i])
        elif GO_SHORT(klines_2h, klines_30m, klines_15m, klines_5m, klines_1m, rsi_trend_5m, rsi_5m, rsi_1m, bb_15m_uptrend, bb_15m_downtrend, bb_5m, bb_1m, is_downtrend_1m, is_downtrend_5m, is_downtrend_15m):
            side = "SHORT"
            binance_futures_api.open_position(i, "SHORT", config.quantity[i])
        else:
            side = "WAITING..."
            print("ACTION           :   🐺 WAITING... 🐺")

    if side != "WAITING...":
        print("config.quantity[i]", config.quantity[i])
        print("Last action executed " + side +" @ " + datetime.now().strftime("%H:%M:%S") + "\n")

    print("= = = CONDITION = = = ")
    try:
        print_entry_condition(side, klines_2h, klines_30m, klines_15m, klines_5m, klines_1m, rsi_trend_5m, rsi_trend_1m, rsi_5m, rsi_1m, bb_5m, bb_1m, is_uptrend_1m, is_uptrend_5m, is_downtrend_1m, is_downtrend_5m)
    except Exception as e:
        print("Error : ", e)
    # if not config.live_trade: 

def hot_zone(klines_30m, klines_1h):
    if klines_30m[-1][0] == klines_1h[-1][0]: return True

def GO_LONG(klines_2h, klines_30m, klines_15m, klines_5m, klines_1m, rsi_trend_5m, rsi_5m, rsi_1m, bb_15m_uptrend, bb_15m_downtrend, bb_5m, bb_1m, trend_1m, trend_5m, trend_15m):
    t1m = trend_1m.is_uptrend.iat[-1]
    t5m = trend_5m.is_uptrend.iat[-1]
    t15m = trend_15m.is_uptrend.iat[-1]
    bbu = bb_15m_uptrend['bb_middle_uptrend'].iat[-1]

    # if t1m: print(colored("GO_LONG 1m:", "green"))
    # if t5m: print(colored("GO_LONG 5m:", "green"))
    # if (t1m & t5m): return True
    # if  hybrid.strong_trend(klines_30m) == "GREEN" and \
    # hybrid.strong_trend(klines_2h) == "GREEN" and \
    #     hybrid.strong_trend(klines_1h) == "GREEN" and \
    # hybrid.strong_trend(klines_15m) == "GREEN" and \
    #     
    #     heikin_ashi.VALID_CANDLE(klines_15m) == "GREEN" and \
    #     
    # is_green = hybrid.strong_trend(klines_5m) == "GREEN" and \
    #     hybrid.strong_trend(klines_1m) == "GREEN" and \
    #     heikin_ashi.VALID_CANDLE(klines_5m) == "GREEN" and \
    #     heikin_ashi.VALID_CANDLE(klines_1m) == "GREEN"
    is30m = heikin_ashi.VALID_CANDLE(klines_30m) == "GREEN"
    is15m = heikin_ashi.VALID_CANDLE(klines_15m) == "GREEN"
    is5m = (heikin_ashi.VALID_CANDLE(klines_5m) == "GREEN" or hybrid.strong_trend(klines_5m) == "GREEN") and \
        (heikin_ashi.VALID_CANDLE(klines_5m) == "GREEN" or hybrid.strong_trend(klines_1m) == "GREEN")
    is1m = heikin_ashi.VALID_CANDLE(klines_1m) == "GREEN"
    is_green = (is30m & is15m & is1m) or (is15m & is5m & is1m)

    # is_not_upper_bb = bb_15m['bb_'] < bb_15m.bb_upperband.iat[-1]
    # is_below_mid_bb = bb_1m.low.iat[-1] <= bb_1m.bb_middleband.iat[-1]
    if  (is_green & (t1m & t5m & t15m & bbu)): return True
    # if  (heikin_ashi.VALID_CANDLE(klines_1m) == "GREEN"): return True
        # (t1m & t5m)) | (rsi_trend_5m == 'RSI_LONG'): return True
        # rsi_5m < config.rsi_buy and rsi_1m < config.rsi_buy: return True

def GO_SHORT(klines_2h, klines_30m, klines_15m, klines_5m, klines_1m, rsi_trend_5m, rsi_5m, rsi_1m, bb_15m_uptrend, bb_15m_downtrend, bb_5m, bb_1m, trend_1m, trend_5m, trend_15m):
    t1m = trend_1m.is_downtrend.iat[-1]
    t5m = trend_5m.is_downtrend.iat[-1]
    t15m = trend_15m.is_downtrend.iat[-1]
    bbd = bb_15m_downtrend['bb_middle_downtrend'].iat[-1]
    # if t1m: print(colored("GO_SHORT 1m:", "red"))
    # if t5m: print(colored("GO_SHORT 5m:", "red"))
    # if (t1m & t5m): return True
    # if  hybrid.strong_trend(klines_1h) == "RED" and \

    # hybrid.strong_trend(klines_2h) == "RED" and \
    #     hybrid.strong_trend(klines_15m) == "RED" and \
    # is_red = hybrid.strong_trend(klines_15m) == "RED" and \
    #     
        # heikin_ashi.VALID_CANDLE(klines_15m) == "RED" and \
        # 
    # is_red = hybrid.strong_trend(klines_5m) == "RED" and \
    #     hybrid.strong_trend(klines_1m) == "RED" and \
    #     heikin_ashi.VALID_CANDLE(klines_5m) == "RED" and \
    #     heikin_ashi.VALID_CANDLE(klines_1m) == "RED"
    is30m = heikin_ashi.VALID_CANDLE(klines_30m) == "RED"
    is15m = heikin_ashi.VALID_CANDLE(klines_15m) == "RED"
    is5m = (heikin_ashi.VALID_CANDLE(klines_5m) == "RED" or hybrid.strong_trend(klines_5m) == "RED") and \
        (heikin_ashi.VALID_CANDLE(klines_5m) == "RED" or hybrid.strong_trend(klines_1m) == "RED")
    is1m = heikin_ashi.VALID_CANDLE(klines_1m) == "RED"
    is_red = (is30m & is15m & is1m) or (is15m & is5m & is1m)
    
    is_red_previous_1m = heikin_ashi.VALID_CANDLE(klines_1m) == "RED"
    is_strong_red =  hybrid.strong_trend(klines_15m) == "RED" and \
        hybrid.strong_trend(klines_5m) == "RED" and \
        hybrid.strong_trend(klines_1m) == "RED"
        # (t1m & t5m) and \

    is_lower_bb = bb_5m.close.iat[-1] > bb_5m.bb_lowerband.iat[-1]
    is_above_mid_bb = bb_5m.low.iat[-1] >= bb_5m.bb_middleband.iat[-1]
    if (is_red & (t1m & t5m & t15m & bbd)): return True
    # if (heikin_ashi.VALID_CANDLE(klines_1m) == "RED"): return True
        # (t1m & t5m)) | (rsi_trend_5m == 'RSI_SHORT'): 
        # rsi_5m > config.rsi_sell and rsi_1m > config.rsi_sell: return True

def EXIT_LONG(response, profit_threshold, klines_5m, klines_1m, rsi_5m, i):
    if (get_position.profit_or_loss(response, profit_threshold) == "PROFIT") & (heikin_ashi.VALID_CANDLE(klines_1m) == "RED"): return True
    elif (heikin_ashi.VALID_CANDLE(klines_5m) == "RED"): return True
    #     return True

def EXIT_SHORT(response, profit_threshold, klines_5m, klines_1m, rsi_5m):
    if (get_position.profit_or_loss(response, profit_threshold) == "PROFIT") & (heikin_ashi.VALID_CANDLE(klines_1m) == "GREEN"): return True
    elif (heikin_ashi.VALID_CANDLE(klines_5m) == "GREEN"): return True
    #     return True
def print_entry_condition(side, klines_2h, klines_30m, klines_15m, klines_5m, klines_1m, rsi_trend_5m, rsi_trend_1m, rsi_5m, rsi_1m, bb_5m, bb_1m, is_uptrend_1m, is_uptrend_5m, is_downtrend_1m, is_downtrend_5m):

    test_color = "RED".upper()
    colour = ""
    if side == "LONG": colour = "green"
    elif side == "SHORT": colour = "red"
    else: colour = "cyan"

    upt_1m = is_uptrend_1m.is_uptrend.iat[-1]
    upt_5m = is_uptrend_5m.is_uptrend.iat[-1]

    dt_1m = is_downtrend_1m.is_downtrend.iat[-1]
    dt_5m = is_downtrend_5m.is_downtrend.iat[-1]

    # is_below_mid_bb = bb_5m.close.iat[-1] < bb_5m.bb_middleband.iat[-1]
    # if is_below_mid_bb: print(colored("GO_SHORT 5m below mid:", "red"))

    # is_above_mid_bb = bb_5m.close.iat[-1] > bb_5m.bb_middleband.iat[-1]
    # if is_above_mid_bb: print(colored("GO_LONG 5m above mid:", "green"))


    # is_not_upper_bb = bb_1m.close.iat[-1] < bb_1m.bb_upperband.iat[-1]
    # print("is_not_upper_bb", is_not_upper_bb)

    # is_not_lower_bb = bb_1m.close.iat[-1] > bb_1m.bb_lowerband.iat[-1]
    # print("is_not_lower_bb", is_not_lower_bb)

    # if side != "WAITING...":
    #     print(colored("2 HR SHORT", colour)) if hybrid.strong_trend(klines_2h) == test_color else print(colored("2 HR LONG", colour))
    #     print(colored("1 HR SHORT", colour)) if hybrid.strong_trend(klines_1h) == test_color else print(colored("1 HR LONG", colour))
    #     print(colored("15 MIN SHORT", colour)) if hybrid.strong_trend(klines_15m) == test_color else print(colored("15 MIN LONG", colour))
    #     print(colored("1 MIN SHORT", colour)) if hybrid.strong_trend(klines_1m) == test_color else print(colored("1 MIN LONG", colour))
    #     print(colored("5 MIN SHORT", colour)) if heikin_ashi.VALID_CANDLE(klines_5m) == test_color else print(colored("5 MIN LONG", colour))
    #     print(colored("1 MIN SHORT", colour)) if heikin_ashi.VALID_CANDLE(klines_1m) == test_color else print(colored("1 MIN LONG", colour))
    
    if side == "LONG":
        print(colored("IS UPTREND 1m YES", "green")) if upt_1m else print(colored("IS UPTREND 1m NO", "cyan"))
        print(colored("IS UPTREND 5m YES", "green")) if upt_5m else print(colored("IS UPTREND 5m NO", "cyan"))
        # print(colored("IS BELOW MID YES", colour)) if bb_5m.low.iat[-1] <= bb_5m.bb_middleband.iat[-1] else print(colored("IS BELOW MID NO", colour))

    if side == "SHORT":
        print(colored("IS DOWNTREND 1m YES", "red")) if dt_1m else print(colored("IS DOWNTREND 1m NO", "cyan"))
        print(colored("IS DOWNTREND 5m YES", "red")) if dt_5m else print(colored("IS DOWNTREND 5m NO", "cyan"))
        # print(colored("IS ABOVE MID YES", colour)) if bb_5m.low.iat[-1] >= bb_5m.bb_middleband.iat[-1] else print(colored("IS ABOVE MID NO", colour))

    print()
    # print(colored("2 HR SHORT STRONG", "red")) if hybrid.strong_trend(klines_2h) == test_color else print(colored("2 HR LONG STRONG", "green"))
    print(colored("30 MIN SHORT STRONG", "red")) if hybrid.strong_trend(klines_30m) == test_color else print(colored("30 MIN LONG STRONG", "green"))
    print(colored("15 MIN SHORT STRONG", "red")) if hybrid.strong_trend(klines_15m) == test_color else print(colored("15 MIN LONG STRONG", "green"))
    print(colored("5 MIN SHORT STRONG", "red")) if hybrid.strong_trend(klines_5m) == test_color else print(colored("5 MIN LONG STRONG", colour))
    print(colored("1 MIN SHORT STRONG", "red")) if hybrid.strong_trend(klines_1m) == test_color else print(colored("1 MIN LONG STRONG", colour))
    print()
    print(colored("30 MIN SHORT VALID", "red")) if heikin_ashi.VALID_CANDLE(klines_30m) == test_color else print(colored("30 MIN LONG VALID", colour))
    print(colored("15 MIN SHORT VALID", "red")) if heikin_ashi.VALID_CANDLE(klines_15m) == test_color else print(colored("15 MIN LONG VALID", "green"))
    print(colored("5 MIN SHORT VALID", "red")) if heikin_ashi.VALID_CANDLE(klines_5m) == test_color else print(colored("5 MIN LONG VALID", colour))
    print(colored("1 MIN SHORT VALID", "red")) if heikin_ashi.VALID_CANDLE(klines_1m) == test_color else print(colored("1 MIN LONG VALID", colour))
    print() 
    if side == "WAITING...":
        if upt_1m & upt_5m:
            print("= = = LONG = = =")
            print(colored("IS UPTREND 1m YES", "green")) if upt_1m else print(colored("IS UPTREND 1m NO", "cyan"))
            print(colored("IS UPTREND 5m YES", "green")) if upt_5m else print(colored("IS UPTREND 5m NO", "cyan"))
            # print(colored("IS BELOW MID 5m YES", "green")) if bb_5m.low.iat[-1] <= bb_5m.bb_middleband.iat[-1] else print(colored("IS BELOW MID 5m NO", "red"))
            # print(colored("IS BELOW MID 1m YES", "green")) if bb_1m.low.iat[-1] <= bb_1m.bb_middleband.iat[-1] else print(colored("IS BELOW MID 1m NO", "red"))
            # long_rsi5m = "LONG 5 MIN RSI " + str(rsi_5m) + " < " + str(config.rsi_buy)
            # print(colored(long_rsi5m, "green" if rsi_5m < config.rsi_buy else "cyan"))
            # long_rsi1m = "LONG 1 MIN RSI " + str(rsi_1m) + " < " + str(config.rsi_buy)
            # print(colored(long_rsi1m, "green" if rsi_1m < config.rsi_buy else "cyan"))
        if dt_5m:
            print("= = = SHORT = = =")
            print(colored("IS DOWNTREND 1m YES", "red")) if dt_1m else print(colored("IS DOWNTREND 1m NO", "cyan"))
            print(colored("IS DOWNTREND 5m YES", "red")) if dt_5m else print(colored("IS DOWNTREND 5m NO", "cyan"))
            # print(colored("IS ABOVE MID 5m YES", "green")) if bb_5m.low.iat[-1] >= bb_5m.bb_middleband.iat[-1] else print(colored("IS ABOVE MID 5m NO", "red"))
            # print(colored("IS ABOVE MID 1m YES", "green")) if bb_1m.low.iat[-1] >= bb_1m.bb_middleband.iat[-1] else print(colored("IS ABOVE MID 1m NO", "red"))
            # short_rsi5m = "SHORT 5 MIN RSI " + str(rsi_5m) + " > " + str(config.rsi_sell)
            # print(colored(short_rsi5m, "green" if rsi_5m > config.rsi_sell else "cyan"))
            # short_rsi1m = "SHORT 1 MIN RSI " + str(rsi_1m) + " > " + str(config.rsi_sell)    
            # print(colored(short_rsi1m, "green" if rsi_1m > config.rsi_sell else "cyan"))

    # print("= = = RSI = = =")
    # rsi_5m_long = rsi_trend_5m == "RSI_LONG"
    # rsi_1m_long = rsi_trend_1m == "RSI_LONG"
    # rsi_5m_short = rsi_trend_5m == "RSI_SHORT"
    # rsi_1m_short = rsi_trend_1m == "RSI_SHORT"

    # if rsi_5m_long | rsi_1m_long:
    #     print(colored("IS RSI 5m LONG", "GREEN")) if rsi_5m_long else print(colored("IS RSI 1m LONG", "GREEN"))
    # elif rsi_5m_short | rsi_1m_short:
    #     print(colored("IS RSI 5m SHORT", "RED")) if rsi_5m_short else print(colored("IS RSI 1m SHORT", "RED"))
    # else:
    #     print(colored("RSI IDLE", "cyan"))
   
    print()
