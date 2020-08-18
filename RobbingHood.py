import robin_stocks as r
import time as t

# Have a file in the directory for your credentials
credFile = open(r"credentials.txt", "Access_Mode")
creds = credFile.readlines()
user = creds[0]
pw = creds[1]
r.login(username=user, password=pw)

# Here we go
# Cancel orders and reset quantity
r.cancel_all_crypto_orders()
priceTracker = list()
while True:
    crypto_positions = r.get_crypto_positions()
    for item in crypto_positions:
        if item['currency']['code'] == 'LTC':
            LTCData = item
    # print(LTCData)
    quantityAvailable = float(LTCData['quantity_available'])
    quantity = float(LTCData['quantity'])
    if quantityAvailable > 0.00:
        # Sell procedure

        print('Starting sell procedure.')
        print('Quantity available to sell: ' + str(quantityAvailable))

        # See what we paid for it
        paid = float(LTCData['cost_bases'][0]['direct_cost_basis'])
        priceBoughtAt = round(paid / quantityAvailable, 2)
        print('Bought at: ' + str(priceBoughtAt))

        # Check price growth
        while len(priceTracker) < 5:
            # Gather more data
            print('Gathering more price data, please wait 5 minutes...')
            t.sleep(60)
            # TODO call a function to gather price data and append to price tracker
            # TODO or, have it run as a thread or something and just sleep until we have enough data

        # TODO change process to look at price changes in last hour (started above)
        # Get starting and current prices
        # print('Fetching prices...')
        # price = r.get_crypto_quote('LTC')
        # openPrice = float(price['open_price'])
        # askPrice = float(price['ask_price'])
        # print('Open Price: ' + str(openPrice))
        # print('Asking: ' + str(askPrice))
        # dayDifference = ((askPrice / openPrice) - 1)
        # print('Day Difference: ' + str(dayDifference * 100) + '%')

        # TODO change process to make decisions based on price changes
        # TODO if trend is downward, wait and gather data until flat or rising
        # Factor in the growth of price for today:
        # If price has gone up, increase percentage that we sell over
        # If price has gone down, decrease percentage that we sell over
        # sellPercent = 1 + round(dayDifference/20, 3)
        # if sellPercent < 1.001:
        #     sellPercent = 1.001
        # print('Sell percentage: ' + str(sellPercent))

        # TODO change process to account for previous wins / losses
        # TODO accrue quantity up to a certain amt and cash out (cap gains)
        # Quantity = win streak. If quantity reaches 150% (possibly change) of initial, cap gains
        # sellPrice = round(priceBoughtAt * sellPercent, 2)
        # print('Selling at: ' + str(sellPrice))
        # print(r.order_sell_crypto_limit('LTC', quantityAvailable, sellPrice, 'gtc'))
        # print('Order placed!')
        # t.sleep(1)

        # Check for sale
        crypto_positions = r.get_crypto_positions()  # Check quantity
        for item in crypto_positions:
            if item['currency']['code'] == 'LTC':
                LTCData = item
        quantity = float(LTCData['quantity'])
        print('Waiting for ' + str(quantity) + ' to sell...')
        while quantity > 0.00:
            t.sleep(15)  # Wait patiently (but not too patiently)
            crypto_positions = r.get_crypto_positions()  # Check quantity again
            for item in crypto_positions:
                if item['currency']['code'] == 'LTC':
                    LTCData = item
            quantity = float(LTCData['quantity'])
        print('All Litecoin sold! Yay!')
    elif quantity <= 0.00:  # No stonks, let's buy
        # Buying procedure
        # TODO repeat changes from selling procedure to buying procedure
        print('Stonks empty, starting buy.')

        # Check price growth

        print('Fetching price...')
        price = r.get_crypto_quote('LTC')
        openPrice = float(price['open_price'])
        markPrice = float(price['mark_price'])
        bidPrice = float(price['bid_price'])
        askPrice = float(price['ask_price'])
        print('Open Price: ' + str(openPrice))
        print('Asking: ' + str(askPrice))
        dayDifference = ((askPrice / openPrice) - 1)
        print('Day Difference: ' + str(round(dayDifference, 2)))

        # Factor in the growth of price for today:
        # If price has gone up, decrease percentage that we buy under
        # If price has gone down, increase percentage that we buy under
        buyPercent = 1 - round(dayDifference/20, 3)
        if buyPercent < 0.999:
            buyPercent = 0.999
        print('Buy percentage: ' + str(buyPercent))
        buyPrice = round(askPrice * buyPercent, 2)
        buyQuantity = round(10.00 / buyPrice, 8)  # Amount of money we're spending / asking price of coin
        print('Bidding price: ' + str(buyPrice))
        print('Quantity buying: ' + str(buyQuantity))
        # print(r.order_buy_crypto_limit('LTC', buyQuantity, buyPrice))
        print('Order placed!')
        t.sleep(1)

        # Check for buy
        crypto_positions = r.get_crypto_positions()
        for item in crypto_positions:
            if item['currency']['code'] == 'LTC':
                LTCData = item
        quantityAvailable = float(LTCData['quantity_available'])
        while quantityAvailable <= 0.00:
            print('Waiting for purchase...')
            t.sleep(15)  # Wait patiently (but not too patiently)
            crypto_positions = r.get_crypto_positions()  # Check quantity again
            for item in crypto_positions:
                if item['currency']['code'] == 'LTC':
                    LTCData = item
            quantityAvailable = float(LTCData['quantity_available'])
        print("We bought Litecoin! Yay! (Don't tell mom)")
    else:  # We have stonks queued to sell, don't touch anything
        # Check for sale
        print("Stonks queued for sale, don't buy until they're done!")  # Them's the rules
        crypto_positions = r.get_crypto_positions()  # Check quantity
        for item in crypto_positions:
            if item['currency']['code'] == 'LTC':
                LTCData = item
        quantity = float(LTCData['quantity'])
        while quantity > 0.00:
            print('Waiting for ' + str(quantity) + ' Litecoin to sell...')
            t.sleep(15)  # Wait patiently (but not too patiently)
            crypto_positions = r.get_crypto_positions()  # Check quantity again
            for item in crypto_positions:
                if item['currency']['code'] == 'LTC':
                    LTCData = item
            quantity = float(LTCData['quantity'])
        print('All Litecoin sold! Yay!')



# streak losses, turn off investing but keep tracking until growth again
# streak wins, increment amount, bank wins at cap
# track changes in last hour, and last five minutes