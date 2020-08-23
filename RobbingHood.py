import robin_stocks as r
import time as t


def Login():
    """Uses a file in the directory called 'credentials.txt' to log in to RobinHood.
    File should have username on line 1 and password on line 2"""
    credfile = open(r"credentials.txt")
    creds = credfile.readlines()
    user = creds[0]
    pw = creds[1]
    r.login(username=user, password=pw)


def SellCryptoBet():
    """Places a bet to sell all available crypto at a higher percent than it was bought.
    Factors in win streak to inflate percentage (sell higher if we've consistently sold higher)"""

    print('Starting sell procedure.')
    print('Quantity available to sell: ' + str(QuantityAvailable))

    # See what we paid for it
    paid = float(LTCData['cost_bases'][0]['direct_cost_basis'])
    priceboughtat = round(paid / QuantityAvailable, 2)
    print('Bought at: ' + str(priceboughtat))

    # Magnify percentage by win streak
    betpercentage = BasePercent + (BasePercent * SellWinStreak)
    print('Bet percentage: ' + str(betpercentage))
    sellprice = round(priceboughtat * (1.000 + (2 * betpercentage)), 2)  # Double percentage because we bought below
    print('Selling at: ' + str(sellprice))
    print(r.order_sell_crypto_limit('LTC', QuantityAvailable, sellprice, 'gtc'))
    print('Order placed!')
    print('')
    t.sleep(5)


def BuyCryptoBet():
    """Places a bet to buy an amount of crypto at a lower price than the current asking.
    Factors in win streak to inflate percentage (buy lower if we've consistently bought lower)"""

    print('Starting buy procedure.')
    print('Money to bet: ' + str(BetAmount))

    # Check price
    print('Fetching price...')
    price = r.get_crypto_quote('LTC')
    askprice = float(price['ask_price'])
    print('Asking: ' + str(askprice))

    # Factor in streak
    betpercentage = BasePercent + (BasePercent * BuyWinStreak)
    print('Bet percentage: ' + str(betpercentage))
    buyprice = round(askprice * (1.000 - betpercentage), 2)
    print('Buying at: ' + str(buyprice))
    buyquantity = round(BetAmount / buyprice, 8)  # Amount of money we're spending / asking price of coin
    print('Quantity buying: ' + str(buyquantity))
    print(r.order_buy_crypto_limit('LTC', buyquantity, buyprice))
    print('Order placed!')
    print('')
    t.sleep(5)


def BuyCryptoImmediately():
    """Buys crypto immediately at the current asking price."""

    print('Starting buy immediate procedure.')
    print('Money to bet: ' + str(BetAmount))

    print('Fetching price...')
    price = r.get_crypto_quote('LTC')
    askprice = float(price['ask_price'])
    print('Asking: ' + str(askprice))
    print(r.order_buy_crypto_by_price('LTC', BetAmount))
    print('Order placed!')
    print('')
    t.sleep(5)


def SellCryptoImmediately():
    """Sells all our crypto immediately at the current asking price."""

    print('Starting sell immediate procedure.')
    print('Quantity available to sell: ' + str(QuantityAvailable))

    # See what we paid for it
    paid = round(float(LTCData['cost_bases'][0]['direct_cost_basis']), 2)
    print('Total amount bet: ' + str(paid))
    priceboughtat = round(paid / QuantityAvailable, 2)
    print('Price bought at: ' + str(priceboughtat))
    print('Fetching price...')
    price = r.get_crypto_quote('LTC')
    askprice = float(price['ask_price'])
    print('Asking: ' + str(askprice))
    print(r.order_sell_crypto_by_quantity('LTC', QuantityAvailable))
    print('Order placed!')
    print('')
    t.sleep(5)


# Here we go
# Cancel orders and reset quantity
Login()
r.cancel_all_crypto_orders()
t.sleep(5)
SellWinStreak = 0
SellLoseStreak = 0
BuyWinStreak = 0
BuyLoseStreak = 0
TimeInterval = 20  # Minutes
BasePercent = 0.001
BetAmount = 10.00  # USD
LoseStreakToQuit = 5
WinStreakToCap = 3

while True:
    crypto_positions = r.get_crypto_positions()
    for item in crypto_positions:
        if item['currency']['code'] == 'LTC':
            LTCData = item
    QuantityAvailable = float(LTCData['quantity_available'])
    Quantity = float(LTCData['quantity'])
    if QuantityAvailable > 0.00:
        # Sell procedure
        SellCryptoBet()
        t.sleep(60 * TimeInterval)

        # Check for sale
        print('Checking sell results...')
        crypto_positions = r.get_crypto_positions()  # Check quantity
        for item in crypto_positions:
            if item['currency']['code'] == 'LTC':
                LTCData = item
        Quantity = float(LTCData['quantity'])
        if Quantity > 0.00:  # Bet was lost
            print('Crypto was not sold. Sad stonk hours.')
            if SellWinStreak > 0:  # Break the streak but reset and try again
                print('Resetting win streak and trying again.')
                r.cancel_all_crypto_orders()
                t.sleep(5)
                SellWinStreak = 0
                SellCryptoBet()
                t.sleep(60 * TimeInterval)
                print('Checking sell results...')
                crypto_positions = r.get_crypto_positions()  # Check quantity
                for item in crypto_positions:
                    if item['currency']['code'] == 'LTC':
                        LTCData = item
                quantity = float(LTCData['quantity'])
                if quantity > 0.00:  # Bet was lost again
                    print('Crypto was not sold. Sell at current price and move on with your life.')
                    print('')
                    r.cancel_all_crypto_orders()
                    t.sleep(5)
                    SellCryptoImmediately()
                    SellLoseStreak += 1
                    if SellLoseStreak >= LoseStreakToQuit:
                        print('Too much loss, throwing a fit and stopping bets.')
                        SystemExit(0)
                else:
                    print('Crypto was sold! Yay!')
                    print('')
                    if SellWinStreak < WinStreakToCap:
                        SellWinStreak += 1
                    SellLoseStreak = 0
            else:  # No streak, take the L
                print('No streak. Sell at current price and move on with your life.')
                print('')
                r.cancel_all_crypto_orders()
                t.sleep(5)
                SellCryptoImmediately()
                SellWinStreak = 0
                SellLoseStreak += 1
                if SellLoseStreak >= LoseStreakToQuit:
                    print('Too much loss, throwing a fit and stopping bets.')
                    SystemExit(0)
        else:  # Bet was won
            print('Crypto was sold! Yay!')
            print('')
            if SellWinStreak < WinStreakToCap:
                SellWinStreak += 1
            SellLoseStreak = 0  # Loop back
    else:  # No stonks, let's buy
        # Buy procedure
        BuyCryptoBet()
        t.sleep(60 * TimeInterval)

        # Check for buy
        print('Checking buy results...')
        crypto_positions = r.get_crypto_positions()  # Check quantity
        for item in crypto_positions:
            if item['currency']['code'] == 'LTC':
                LTCData = item
        QuantityAvailable = float(LTCData['quantity_available'])
        if QuantityAvailable <= 0.00:  # Bet was lost
            print('Crypto was not bought. Sad stonk hours.')
            if BuyWinStreak > 0:  # Break the streak but reset and try again
                print('Resetting win streak and trying again.')
                r.cancel_all_crypto_orders()
                t.sleep(5)
                BuyWinStreak = 0
                BuyCryptoBet()
                t.sleep(60 * TimeInterval)
                print('Checking buy results...')
                crypto_positions = r.get_crypto_positions()  # Check quantity
                for item in crypto_positions:
                    if item['currency']['code'] == 'LTC':
                        LTCData = item
                QuantityAvailable = float(LTCData['quantity_available'])
                if QuantityAvailable <= 0.00:  # Bet was lost again
                    print('Crypto was not bought. Buy at current price and move on with your life.')
                    print('')
                    r.cancel_all_crypto_orders()
                    t.sleep(5)
                    BuyWinStreak = 0
                    BuyLoseStreak += 1
                    BuyCryptoImmediately()
                else:
                    print('Crypto was bought! Yay!')
                    print('')
                    if BuyWinStreak < WinStreakToCap:
                        BuyWinStreak += 1
                    BuyLoseStreak = 0
            else:  # No streak, take the L
                print('No streak. Buy at current price and move on with your life.')
                print('')
                r.cancel_all_crypto_orders()
                t.sleep(5)
                BuyWinStreak = 0
                BuyLoseStreak += 1
                BuyCryptoImmediately()
        else:  # Bet was won
            print('Crypto was bought! Yay!')
            print('')
            if BuyWinStreak < WinStreakToCap:
                BuyWinStreak += 1
            BuyLoseStreak = 0
