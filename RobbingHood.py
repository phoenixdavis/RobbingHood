import robin_stocks as r
import time as t

r.login(username='phoenixdd13@gmail.com', password='nixthegreat13')
while True:
    crypto_positions = r.get_crypto_positions()
    for item in crypto_positions:
        if item['currency']['code'] == 'LTC':
            LTCData = item
    # print(LTCData)
    quantityAvailable = float(LTCData['quantity_available'])
    quantity = float(LTCData['quantity'])
    print('Quantity: ' + str(quantity))
    print('Quantity Available: ' + str(quantityAvailable))
    if quantityAvailable > 0.00:
        print('Quantity available to sell: ' + str(quantityAvailable))
        paid = float(LTCData['cost_bases'][0]['direct_cost_basis'])
        priceBoughtAt = round(paid / quantityAvailable, 2)
        print('Bought at: ' + str(priceBoughtAt))

        print('Fetching price...')
        price = r.get_crypto_quote('LTC')
        openPrice = float(price['open_price'])
        markPrice = float(price['mark_price'])
        bidPrice = float(price['bid_price'])
        askPrice = float(price['ask_price'])
        print('Open Price: ' + str(openPrice))
        print('Asking: ' + str(askPrice))
        dayDifference = ((askPrice / openPrice) - 1)
        print('Day Difference: ' + str(dayDifference))

        # Factor in the growth of price for today:
        # If price has gone up, increase percentage that we sell over
        # If price has gone down, decrease percentage that we sell over
        sellPercent = 1 + round(dayDifference/20, 3)
        if sellPercent < 1.001:
            sellPercent = 1.001
        print('Sell percentage: ' + str(sellPercent))

        sellPrice = round(priceBoughtAt * sellPercent, 2)
        print('Selling at: ' + str(sellPrice))
        print(r.order_sell_crypto_limit('LTC', quantityAvailable, sellPrice, 'gtc'))
        print('Order placed!')
        t.sleep(1)

        # Check for sale
        crypto_positions = r.get_crypto_positions()  # Check quantity
        for item in crypto_positions:
            if item['currency']['code'] == 'LTC':
                LTCData = item
        quantity = float(LTCData['quantity'])
        while quantity > 0.00:
            print('Waiting for ' + str(quantity) + ' to sell...')
            t.sleep(15)  # Wait patiently (but not too patiently)
            crypto_positions = r.get_crypto_positions()  # Check quantity again
            for item in crypto_positions:
                if item['currency']['code'] == 'LTC':
                    LTCData = item
            quantity = float(LTCData['quantity'])
        print('All Litecoin sold! Yay!')

    elif quantity <= 0.00:  # No stonks, let's buy
        print('Stonks empty, starting buy.')
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
        print(r.order_buy_crypto_limit('LTC', buyQuantity, buyPrice))
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
    else:  # We have stonks queued to sell, don't fucking touch anything
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
