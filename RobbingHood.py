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
        if i['currency']['code'] == CryptoSymbol:
            quantity = float(i['quantity_available'])
            return quantity
    return -1.0


def GetQuantity():
    pos = r.get_crypto_positions()
    for i in pos:
        if i['currency']['code'] == CryptoSymbol:
            quantity = float(i['quantity'])
            return quantity
    return -1.0


def GetBet():
    pos = r.get_crypto_positions()
    for i in pos:
        if i['currency']['code'] == CryptoSymbol:
            return float(i['cost_bases'][0]['direct_cost_basis'])
    return -1.0


def GetState(orderid):
    order = r.get_crypto_order_info(orderid)
    return order['state']


def SellCryptoBet():
    """Places a bet to sell all available crypto at a higher percent than it was bought.
    Factors in win streak to inflate percentage (sell higher if we've consistently sold higher)"""

    print('Starting sell procedure.')
    quantityavailable = GetQuantityAvailable()
    if quantityavailable <= 0:
        print('Called Sell without anything to sell! Stopping.')
        exit(-69)
    print('Quantity available to sell: ' + str(quantityavailable))
    paid = GetBet()
    priceboughtat = round(paid / quantityavailable, 2)
    print('Bought at: ' + str(priceboughtat))
    betpercentage = BasePercent + (BasePercent * SellWinStreak)
    print('Bet percentage: ' + str(betpercentage))
    sellprice = round(priceboughtat * (1.000 + betpercentage), 2)
    print('Selling at: ' + str(sellprice))
    price = r.get_crypto_quote(CryptoSymbol)
    askprice = float(price['ask_price'])
    print('Current asking: ' + str(askprice))
    orderinfo = (r.order_sell_crypto_limit(CryptoSymbol, quantityavailable, sellprice, 'gtc'))
    print('Order placed!')
    print('')
    orderid = orderinfo['id']
    success = Wait(orderid, False, False)
    print('Checking sell results...')
    if not success:
        CancelOrders(orderid)
        print('Sell failure.')
    else:
        print('Sell success!')
    print('')
    return success


def BuyCryptoBet(bet):
    """Places a bet to buy an amount of crypto at a lower price than the current asking."""

    print('Starting buy procedure.')
    price = r.get_crypto_quote(CryptoSymbol)
    askprice = float(price['ask_price'])
    print('Asking: ' + str(askprice))
    betpercentage = BasePercent
    buyprice = round(askprice * (1.000 - betpercentage), 2)
    print('Buying at: ' + str(buyprice))
    buyquantity = round(bet / buyprice, 8)  # Amount of money we're spending / asking price of coin
    print('Quantity buying: ' + str(buyquantity))
    orderinfo = r.order_buy_crypto_limit(CryptoSymbol, buyquantity, buyprice)
    orderid = orderinfo['id']
    print('Order placed!')
    print('')
    success = Wait(orderid, False, True)
    print('Checking buy results...')
    if not success:
        CancelOrders(orderid)
        print('Buy failure.')
    else:
        print('Buy success!')
    print('')
    return success


def BuyCryptoImmediately(bet):
    """Buys crypto immediately at the current asking price."""

    print('Starting Immediate Buy procedure...')
    print('Money to bet: ' + str(bet))
    price = r.get_crypto_quote(CryptoSymbol)
    ask_price = float(price['ask_price'])
    print('Asking: ' + str(ask_price))
    print('Placing order...')
    orderinfo = r.order_buy_crypto_by_price(CryptoSymbol, bet)
    orderid = orderinfo['id']
    Wait(orderid, True, True)
    print('Bought!')
    print('')


def SellCryptoImmediately():
    """Sells all our crypto immediately at the current asking price."""

    print('Starting Immediate Sell procedure...')
    quantityavailable = GetQuantityAvailable()
    if quantityavailable <= 0:
        print('Called Sell Immediate without anything to sell! Stopping.')
        exit(-69)
    print('Quantity available to sell: ' + str(quantityavailable))
    paid = GetBet()
    print('Total amount bet: ' + str(paid))
    priceboughtat = round(paid / quantityavailable, 2)
    print('Price bought at: ' + str(priceboughtat))
    price = r.get_crypto_quote(CryptoSymbol)
    bid_price = float(price['bid_price'])
    print('Bidding: ' + str(bid_price))
    loss = paid - (paid * (bid_price / priceboughtat))
    loss = round(loss, 2)
    print('Estimated losses: ' + str(loss))
    print('Placing order...')
    orderinfo = r.order_sell_crypto_by_quantity(CryptoSymbol, quantityavailable, priceType='bid_price')
    orderid = orderinfo['id']
    Wait(orderid, True, False)
    print('Sold!')
    print('')


def Wait(orderid, immediate, buying):
    """Waits until TimeInterval is reached or order is filled. If immediate, run forever (should trigger immediately)."""

    print('Begin wait...')
    if immediate:
        state = GetState(orderid)
        while state != 'filled':
            print('\rWaiting for immediate order to fulfill. State: ' + state, end='')
            t.sleep(15)
            state = GetState(orderid)
        print('')
        return True
    else:
        time = 0
        if buying:
            endtime = 300
        else:
            endtime = TimeInterval
        state = GetState(orderid)
        while time < endtime:
            if state != 'filled':
                print('\rWaiting for order to fulfill. State: ' + state + ', Time: ' + str(time) + 's', end='')
                t.sleep(15)
                time += 15
                state = GetState(orderid)
            else:
                print('')
                return True
        print('')
        return False


def StartCryptoContract():
    """Takes current coin and makes limit order to sell above purchased price"""

    print('Starting contract creation procedure...')
    quantityavailable = GetQuantityAvailable()
    print('Quantity available: ' + str(quantityavailable))
    paid = GetBet() / ActiveContracts
    priceboughtat = round(paid / quantityavailable, 2)
    print('Bought at: ' + str(priceboughtat))
    sellprice = round(priceboughtat * (1.0000 + BasePercent), 2)
    print('Selling at: ' + str(sellprice))
    orderinfo = (r.order_sell_crypto_limit(CryptoSymbol, quantityavailable, sellprice, 'gtc'))
    print('Contract created!')
    print('')
    orderid = orderinfo['id']
    return orderid


def ContractWait():
    """Waits until TimeInterval is reached or a contract is sold. Periodically checks contracts"""

    time = 0
    print(ContractIDs)
    while time < TimeInterval:
        remove = []
        for contractid in ContractIDs:
            if GetState(contractid) == 'filled':
                remove.append(contractid)
        if len(remove) > 0:
            print('')
            print('Contract(s) sold!')
            for contractid in remove:
                ContractIDs.remove(contractid)
            return True
        else:
            print('\rWaiting for contracts to sell. Time: ' + str(time) + 's', end='')
            t.sleep(15)
            time += 15
    print('')
    print('No contracts sold.')
    return False


def CancelOrders(orderid=''):
    """Cancels order if id is given. If no id is given, cancels all orders. Returns when completed"""

    if orderid == '':
        r.cancel_all_crypto_orders()
        t.sleep(5)
        while len(r.get_all_open_crypto_orders()) != 0:
            t.sleep(10)
    else:
        r.cancel_crypto_order(orderid)
        t.sleep(5)
        state = GetState(orderid)
        while state != 'canceled':
            t.sleep(10)
            state = GetState(orderid)


# Here we go
# Cancel orders and reset quantity
print('Booting up degen DeFi strategies....')
t.sleep(0.5)
print('Taunting Warren Buffett...')
t.sleep(0.5)
print('Making money printer go brrr..')
t.sleep(0.5)
Login()
print('We\'re in.\n')
CryptoSymbol = 'LTC'
print('Checking orders..')
if len(r.get_all_open_crypto_orders()) != 0:
    print('Canceling orders..')
    r.cancel_all_crypto_orders()
else:
    print('No orders.')
t.sleep(2)
print('Checking coin..')
QuantityAvailable = GetQuantityAvailable()
if QuantityAvailable > 0.00:
    print('Selling all existing coin..')
    SellCryptoImmediately()
else:
    print('Coin empty.')
print('')
print('Which gambling strategy would you like to lose money with today?')
print('1 - Vanilla')
print('2 - Pseudo Stop Loss')
print('3 - YOLO all your funds into $TSLA')
choice = input('Input: ')
print('')

if choice == '1':
    print('Welcome to Vanilla:')
    print('Reliable, but not as fun as you remember.')
    print('Would you like to run manually or automatically? M/A')
    choice = input('Input: ')
    print('')
    Mode = 'M'
    if choice == 'M':
        print('Starting in manual mode.')
        Mode = 'M'
    elif choice == 'A':
        print('Starting in automatic mode.')
        Mode = 'A'
    else:
        print('You\'re an idiot. Starting in manual mode.')
        Mode = 'M'

    SellWinStreak = 0
    SellLoseStreak = 0
    TimeInterval = 1000  # Seconds
    BasePercent = 0.0015
    BetAmount = 50.00  # USD
    LoseStreakToQuit = 4
    WinStreakToCap = 3

    while True:
        # Buy procedure
        # bought = BuyCryptoBet(BetAmount)
        # if not bought:  # Bet was lost
        #     print('Buy at current asking price and move on.\n')
        #     BuyCryptoImmediately(BetAmount)
        BuyCryptoImmediately(BetAmount)

        # Sell procedure
        sold = SellCryptoBet()
        if sold:
            if SellWinStreak < WinStreakToCap:
                SellWinStreak += 1
            SellLoseStreak = 0
        else:  # Bet was lost
            if SellWinStreak > 0:  # Break the streak but reset and try again
                print('Resetting win streak and trying again...\n')
                SellWinStreak = 0
                sold = SellCryptoBet()
                if sold:
                    if SellWinStreak < WinStreakToCap:
                        SellWinStreak += 1
                    SellLoseStreak = 0
                else:  # Bet was lost again
                    print('Sell at current price and move on.\n')
                    SellCryptoImmediately()
                    SellLoseStreak += 1
                    SellWinStreak = 0
            else:  # No streak, take the L
                print('No streak. Admitting defeat.\n')
                SellCryptoImmediately()
                SellWinStreak = 0
                SellLoseStreak += 1

        # Check losses
        if SellLoseStreak >= LoseStreakToQuit:
            print('Too much loss, throwing a fit and stopping bets.')
            exit(-1)

        if Mode == 'M':
            print('Bet finished. Continue? (Y/N)')
            if input('Input: ') == 'N':
                print('Pussy.')
                exit(-1)
            else:
                print('Forging on.')
                print('')
        else:
            print('Restarting procedure..')
            t.sleep(5)
elif choice == '2':
    print('Welcome to Pseudo Stop Loss.')
    print('Pseudo because it won''t actually stop losses.\n')

    ActiveContracts = 0
    MaxContracts = 5
    BetAmount = 20.00
    BasePercent = 0.0050
    LoseStreakToQuit = 4
    LoseStreak = 0
    TimeInterval = 3600  # Seconds
    ContractIDs = []

    while True:
        if ActiveContracts < MaxContracts:  # Add a contract
            print('Let''s add a contract.')
            BuyCryptoImmediately(BetAmount)
            ActiveContracts += 1
            ContractIDs.append(StartCryptoContract())
            sold = ContractWait()  # Let contract(s) cook
            ActiveContracts = len(ContractIDs)
            if sold:
                LoseStreak = 0
            print('')
        else:  # Max contracts, drop one
            print('Let''s drop a contract.')
            CancelOrders(ContractIDs[0])
            ContractIDs = ContractIDs[1:4]
            ActiveContracts -= 1
            LoseStreak += 1
            print('')
            # Check losses
            if LoseStreak >= LoseStreakToQuit:
                print('Too much loss, throwing a fit and stopping bets.')
                exit(1337)
elif choice == '3':
    print('Giving praise to Papa Elon...')
    t.sleep(1)
    exit(420)
else:
    print('Idk how you managed to fuck that up but I''m leaving.')
    exit(69)
