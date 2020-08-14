import robin_stocks as r
import pandas as pd
import time as t

r.login(username='phoenixdd13@gmail.com', password='nixthegreat13')

crypto_positions = r.get_crypto_positions()
for item in crypto_positions:
    if item['currency']['code'] == 'LTC':
        LTCData = item
# print(LTCData)
quantityAvailable = float(LTCData['quantity_available'])
quantity = float(LTCData['quantity'])
if quantityAvailable > 0.00:
    print('Quantity available to sell: ' + str(quantityAvailable))
    paid = float(LTCData['cost_bases'][0]['direct_cost_basis'])
    priceBoughtAt = round(paid / quantityAvailable, 2)
    print('Bought at: ' + str(priceBoughtAt))
    sellPrice = round(priceBoughtAt * 1.002, 2)
    print('Selling at: ' + str(sellPrice))
    # print(r.order_sell_crypto_limit('LTC', quantityAvailable, sellPrice, 'gtc'))
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
elif quantity <= 0.00:  # No stonks available, check it we have some queued to sell
    print('Stonks empty, starting buy.')
    print('Fetching price...')
    price = r.get_crypto_quote('LTC')
    openPrice = float(price['open_price'])
    markPrice = float(price['mark_price'])
    bidPrice = float(price['bid_price'])
    askPrice = float(price['ask_price'])
    print('Open Price: ' + str(openPrice))
    print('Asking: ' + str(askPrice))
    print('Bidding: ' + str(bidPrice))
    print('Marked: ' + str(markPrice))
    print('Day Difference: ' + str(openPrice - askPrice))
    buyPrice = askPrice * 0.998
    buyQuantity = 1.00 / askPrice
    print('Buying at -0.2% bidding price: ' + str(buyPrice))
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
        quantity = float(LTCData['quantity_available'])
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
        print('Waiting for ' + str(quantity) + ' to sell...')
        t.sleep(15)  # Wait patiently (but not too patiently)
        crypto_positions = r.get_crypto_positions()  # Check quantity again
        for item in crypto_positions:
            if item['currency']['code'] == 'LTC':
                LTCData = item
        quantity = float(LTCData['quantity'])
    print('All Litecoin sold! Yay!')
