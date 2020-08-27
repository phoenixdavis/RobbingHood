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
            return float(i['quantity_available'])
    return -1.0


def GetQuantity():
    pos = r.get_crypto_positions(info='quantity')
    for i in pos:
        if i['currency']['code'] == 'LTC':
            return float(i['quantity'])
    return -1.0


def GetBet():
    pos = r.get_crypto_positions()
    for i in pos:
        if i['currency']['code'] == 'LTC':
            return float(i['cost_bases'][0]['direct_cost_basis'])
    return -1.0


def GetState(orderid):
    print('Loading profile...')
    Login()
    print('Fetching order info...')
    order = r.get_crypto_order_info(orderid)
    print(order)
    print('Returning state...')
    print(order['state'])
    return order['state']


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
    orderinfo = (r.order_sell_crypto_limit('LTC', quantityavailable, sellprice, 'gtc'))
    print('Order placed!')
    print('')
    orderid = orderinfo['id']
    success = Wait(orderid, False)
    print('Checking sell results...')
    if not success:
        r.cancel_crypto_order(orderid)
        print('Sell failure.')
    else:
        print('Sell success!')
    print('')
    return success


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
    orderinfo = r.order_buy_crypto_limit('LTC', buyquantity, buyprice)
    orderid = orderinfo['id']
    print('Order placed!')
    print('')
    success = Wait(orderid, False)
    print('Checking buy results...')
    if not success:
        r.cancel_crypto_order(orderid)
        print('Buy failure.')
    else:
        print('Buy success!')
    print('')
    return success


def BuyCryptoImmediately():
    """Buys crypto immediately at the current asking price."""

    print('Starting Immediate Buy procedure...')
    print('Money to bet: ' + str(BetAmount))
    price = r.get_crypto_quote('LTC')
    askprice = float(price['ask_price'])
    print('Asking: ' + str(askprice))
    orderinfo = r.order_buy_crypto_by_price('LTC', BetAmount)
    orderid = orderinfo['id']
    print('Order placed!')
    Wait(orderid, True)
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
    orderinfo = r.order_sell_crypto_by_quantity('LTC', quantityavailable)
    orderid = orderinfo['id']
    print('Order placed!')
    Wait(orderid, True)
    print('Sold!')
    print('')


def Wait(orderid, immediate):
    if immediate:
        state = GetState(orderid)
        while state != 'filled':
            print('Waiting for order to fulfill...')
            t.sleep(60)
            state = GetState(orderid)
        return True
    else:
        time = 0
        state = GetState(orderid)
        while time < TimeInterval:
            if state != 'filled':
                t.sleep(60)
                time += 60
                state = GetState(orderid)
            else:
                return True
        return False


# Here we go
# Cancel orders and reset quantity
print('Booting up degen DeFi strategies....')
t.sleep(2)
print('Taunting Warren Buffett...')
t.sleep(2)
print('Making money printer go brrr..')
t.sleep(2)
Login()
print('We''re in.')
r.cancel_all_crypto_orders()
t.sleep(5)
QuantityAvailable = GetQuantityAvailable()
if QuantityAvailable > 0.00:
    print('Selling all existing coin..')
    SellCryptoImmediately()

print('')
print('Which gambling strategy would you like to lose money on today?')
print('1 - Vanilla')
print('2 - Pseudo Stop Loss\n')
choice = input('')
print('')

if choice == '1':
    print('Welcome to Vanilla.')
    print('Reliable, but not as good as you remember.\n')

    SellWinStreak = 0
    SellLoseStreak = 0
    TimeInterval = 2400  # Seconds
    BasePercent = 0.0015
    BetAmount = 20.00  # USD
    LoseStreakToQuit = 4
    WinStreakToCap = 3

    while True:
        # Buy procedure
        bought = BuyCryptoBet()
        if not bought:  # Bet was lost
            print('Buy at current asking price and move on.')
            print('')
            BuyCryptoImmediately()

        # Sell procedure
        sold = SellCryptoBet()
        if not sold:  # Bet was lost
            if SellWinStreak > 0:  # Break the streak but reset and try again
                print('Resetting win streak and trying again...')
                print('')
                SellWinStreak = 0
                sold = SellCryptoBet()
                if not sold:  # Bet was lost again
                    print('Sell at current price and move on.\n')
                    SellCryptoImmediately()
                    SellLoseStreak += 1
                    if SellWinStreak < WinStreakToCap:
                        SellWinStreak += 1
                    SellLoseStreak = 0
            else:  # No streak, take the L
                print('No streak. Admitting defeat.\n')
                SellCryptoImmediately()
                SellWinStreak = 0
                SellLoseStreak += 1

        # Check losses
        if SellLoseStreak >= LoseStreakToQuit:
            print('Too much loss, throwing a fit and stopping bets.')
            SystemExit(-666)

elif choice == '2':
    print('Welcome to Pseudo Stop Loss.')
    print('Pseudo because it won''t actually stop losses.\n')
else:
    print('Idk how you managed to fuck that up. Don''t ever buy stonks.')
    exit(-69)
