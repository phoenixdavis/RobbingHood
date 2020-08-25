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


def GetQuantityAvailable():
    pos = r.get_crypto_positions()
    for i in pos:
        if i['currency']['code'] == 'LTC':
            data = i
    return float(data['quantity_available'])


def GetQuantity():
    pos = r.get_crypto_positions()
    for i in pos:
        if i['currency']['code'] == 'LTC':
            data = i
    return float(data['quantity'])


def GetBet():
    pos = r.get_crypto_positions()
    for i in pos:
        if i['currency']['code'] == 'LTC':
            data = i
    return float(data['cost_bases'][0]['direct_cost_basis'])


def SellCryptoBet():
    """Places a bet to sell all available crypto at a higher percent than it was bought.
    Factors in win streak to inflate percentage (sell higher if we've consistently sold higher)"""

    print('Starting sell procedure.')
    quantityavailable = GetQuantityAvailable()
    print('Quantity available to sell: ' + str(quantityavailable))
    paid = GetBet()
    priceboughtat = round(paid / quantityavailable, 2)
    print('Bought at: ' + str(priceboughtat))
    betpercentage = BasePercent + (BasePercent * SellWinStreak)
    print('Bet percentage: ' + str(betpercentage))
    sellprice = round(priceboughtat * (1.000 + betpercentage), 2)
    print('Selling at: ' + str(sellprice))
    print(r.order_sell_crypto_limit('LTC', quantityavailable, sellprice, 'gtc'))
    print('Order placed!')
    print('')
    Wait(True, False)
    print('Checking sell results...')
    quantity = GetQuantity()
    return quantity == 0.00


def BuyCryptoBet():
    """Places a bet to buy an amount of crypto at a lower price than the current asking."""

    print('Starting buy procedure.')
    price = r.get_crypto_quote('LTC')
    askprice = float(price['ask_price'])
    print('Asking: ' + str(askprice))
    betpercentage = BasePercent
    buyprice = round(askprice * (1.000 - betpercentage), 2)
    print('Buying at: ' + str(buyprice))
    buyquantity = round(BetAmount / buyprice, 8)  # Amount of money we're spending / asking price of coin
    print('Quantity buying: ' + str(buyquantity))
    print(r.order_buy_crypto_limit('LTC', buyquantity, buyprice))
    print('Order placed!')
    print('')
    Wait(False, False)
    print('Checking buy results...')
    quantityavailable = GetQuantityAvailable()
    return quantityavailable > 0.00


def BuyCryptoImmediately():
    """Buys crypto immediately at the current asking price."""

    print('Starting Immediate Buy procedure...')
    print('Money to bet: ' + str(BetAmount))
    price = r.get_crypto_quote('LTC')
    askprice = float(price['ask_price'])
    print('Asking: ' + str(askprice))
    print(r.order_buy_crypto_by_price('LTC', BetAmount))
    print('Order placed!')
    Wait(False, True)
    print('Bought!')
    print('')


def SellCryptoImmediately():
    """Sells all our crypto immediately at the current asking price."""

    print('Starting Immediate Sell procedure...')
    quantityavailable = GetQuantityAvailable()
    print('Quantity available to sell: ' + str(quantityavailable))
    paid = GetBet()
    print('Total amount bet: ' + str(paid))
    priceboughtat = round(paid / quantityavailable, 2)
    print('Price bought at: ' + str(priceboughtat))
    price = r.get_crypto_quote('LTC')
    askprice = float(price['ask_price'])
    print('Asking: ' + str(askprice))
    loss = askprice / priceboughtat * 100
    loss = round(loss * priceboughtat, 2)
    print('Estimated loss: ' + str(loss))
    print(r.order_sell_crypto_by_quantity('LTC', quantityavailable))
    print('Order placed!')
    Wait(True, True)
    print('Sold!')
    print('')


def Wait(issale, isimmediate):
    time = 0
    if issale:  # Sale
        quantity = GetQuantity()
        if isimmediate:
            while quantity != 0:
                print('Waiting for ' + str(quantity) + ' to sell...')
                t.sleep(60)
                quantity = GetQuantity()
        else:
            while time < TimeInterval:
                if quantity != 0:  # No sale
                    t.sleep(60)
                    time += 60
                    quantity = GetQuantity()
                else:
                    break
    else:  # Buy
        quantityavailable = GetQuantityAvailable()
        if isimmediate:
            while quantityavailable == 0:
                print('Waiting for coin to be bought...')
                t.sleep(60)
                quantityavailable = GetQuantityAvailable()
        else:
            while time < TimeInterval:
                if quantityavailable == 0:  # No buy
                    t.sleep(60)
                    time += 60
                    quantityavailable = GetQuantityAvailable()
                else:
                    break


# Here we go
# Cancel orders and reset quantity
Login()
r.cancel_all_crypto_orders()
t.sleep(5)
SellWinStreak = 0
SellLoseStreak = 0
TimeInterval = 2400  # Seconds
BasePercent = 0.0015
BetAmount = 20.00  # USD
LoseStreakToQuit = 5
WinStreakToCap = 3

while True:
    QuantityAvailable = GetQuantityAvailable()
    Quantity = GetQuantity()
    if QuantityAvailable > 0.00:
        # Sell procedure
        sold = SellCryptoBet()
        if not sold:  # Bet was lost
            print('No sale. Sad stonk hours.')
            if SellWinStreak > 0:  # Break the streak but reset and try again
                print('Resetting win streak and trying again...')
                print('')
                r.cancel_all_crypto_orders()
                SellWinStreak = 0
                sold = SellCryptoBet()
                if not sold:  # Bet was lost again
                    print('No sale. Sell at current price and move on with your life.')
                    print('')
                    r.cancel_all_crypto_orders()
                    SellCryptoImmediately()
                    SellLoseStreak += 1
                    if SellLoseStreak >= LoseStreakToQuit:
                        print('Too much loss, throwing a fit and stopping bets.')
                        SystemExit(0)
                else:
                    print('Sold! Yay!')
                    print('')
                    if SellWinStreak < WinStreakToCap:
                        SellWinStreak += 1
                    SellLoseStreak = 0
            else:  # No streak, take the L
                print('No streak. Sell at current price and move on.')
                print('')
                r.cancel_all_crypto_orders()
                SellCryptoImmediately()
                SellWinStreak = 0
                SellLoseStreak += 1
                if SellLoseStreak >= LoseStreakToQuit:
                    print('Too much loss, throwing a fit and stopping bets.')
                    SystemExit(0)
        else:  # Bet was won
            print('Sold! Yay!')
            print('')
            if SellWinStreak < WinStreakToCap:
                SellWinStreak += 1
            SellLoseStreak = 0

    else:  # No stonks, let's buy
        bought = BuyCryptoBet()
        if not bought:  # Bet was lost
            print('Crypto was not bought. Sad stonk hours.')
            print('Buy at current asking price and move on.')
            print('')
            r.cancel_all_crypto_orders()
            BuyCryptoImmediately()
        else:  # Bet was won
            print('Crypto was bought! Yay!')
            print('')
