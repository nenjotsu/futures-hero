while True:
    print("\nHere are the supported Pairs: ")
    print("1. BTC-USDT")
    print("2. ETH-USDT")
    print("3. LTC-USDT")

    input_pair = input("\nChoose your Pair :   ").upper() or 'BTC'

    if (input_pair == '1') or (input_pair == 'BTC'):
        coin            = "BTC"
        quantity        = 0.003     # 1USDT == 0.003 BTC @ 37XXX
        leverage        = 125       # Maximum 125
        threshold       = 0.15      # Optimal 0.15 for entry
        stoplimit       = 0.10      # shall be 70-100% of threshold
        callbackRate    = 0.2
        round_decimal   = 2
        break

    elif (input_pair == '2') or (input_pair == 'ETH'):
        coin            = "ETH"
        quantity        = 0.07      # 1USDT == 0.07 ETH @ 1400
        leverage        = 100       # Maximum 100
        threshold       = 0.15
        stoplimit       = 0.10
        callbackRate    = 0.2
        round_decimal   = 2
        break

    elif (input_pair == '3') or (input_pair == 'LTC'):
        coin            = "LTC"
        quantity        = 0.4       # 1USDT == 0.4 LTC @ 165
        leverage        = 75        # Maximum 75
        threshold       = 0.15
        stoplimit       = 0.10
        callbackRate    = 0.2
        round_decimal   = 2
        break

    elif (input_pair == '4') or (input_pair == 'BCH'):
        coin            = "BCH"
        quantity        = 0.12      # 1USDT == 0.12 BCH @ 535
        leverage        = 75        # Maximum 75
        threshold       = 0.15
        stoplimit       = 0.08
        callbackRate    = 0.2
        round_decimal   = 2
        break

    else: print("❗Invalid Number❗Try again❗\n")

pair = coin + "USDT"

print("Pair Name        :   " + str(pair))
print("Trade Quantity   :   " + str(quantity) + " " + str(coin))
print("Leverage         :   " + str(leverage) + "x")
print("Price Movement   :   " + str(threshold) + " %")
print("Stop Limit       :   " + str(stoplimit) + " %")
print("Round Decimal    :   " + str(round_decimal) + " decimal place")
print()
