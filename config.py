
live_trade = True

coin     = ["RAY"]
quantity = [1]
coin_decimal = 3.0
# coin     = ["BTC"]
# quantity = [0.0005]
# quantity = [0130/20
# coin     = ["SOL"]
# quantity = [2]
strategy = 'strategy_ema'

ema_short = 50
ema_long = 200

# profit_margin * leverage = Actual Profit Percentage.
take_profit_percentage = 0.4
profit_margin = 0.2
rsi_buy = 60
rsi_sell = 70

mfi_buy = 32
mfi_sell = 78

bb_buy = 0.02
bb_sell = 0.89

# ====================================================
#        !! DO NOT CHANGE THE LEVERAGE !!
# ====================================================
leverage, pair = [], []
for i in range(len(coin)):
    pair.append(coin[i] + "USDT")
    if   coin[i] == "BTC": leverage.append(50)
    elif coin[i] == "ETH": leverage.append(40)
    else: leverage.append(1)

    print("Pair Name        :   " + pair[i])
    print("Trade Quantity   :   " + str(quantity[i]) + " " + coin[i])
    print("Leverage         :   " + str(leverage[i]))
    print()
