import time
import requests
import hmac
from hashlib import sha256
import time
from datetime import datetime, timedelta

APIURL = "https://open-api.bingx.com"
# APIKEY = // Some sensitive logic was here
# SECRETKEY = // Some sensitive logic was here
# symbol= // Some sensitive logic was here
# leverage = // Some sensitive logic was here
# account_value = // Some sensitive logic was here
# start_margin = // Some sensitive logic was here
# start_notional_value = // Some sensitive logic was here
# stop_loss_price = // Some sensitive logic was here
# take_profit_price = // Some sensitive logic was here
# int_round = // Some sensitive logic was here

def notify_order(message):
    # bot_token = // Some sensitive logic was here
    # chat_id = // Some sensitive logic was here
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=payload)

def notify_status(message):
    # bot_token = // Some sensitive logic was here
    # chat_id = // Some sensitive logic was here
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=payload)

def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    return signature

def send_request(method, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload)
    return response.json()

def parseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    if paramsStr != "":
     return paramsStr+"&timestamp="+str(int(time.time() * 1000))
    else:
     return paramsStr+"timestamp="+str(int(time.time() * 1000))

def calculate_quantity(notional_value, price):
    if price <= 0:
        print("Price must be greater than zero")
    return notional_value / price


def account_data():
    payload = {}
    path = '/openApi/swap/v3/user/balance'
    method = "GET"
    paramsMap = {
    "timestamp": int(time.time() * 1000)
}
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def get_balance():
    response = account_data()
    if response.get('code') == 0 and 'data' in response:
        for item in response['data']:
            if item['asset'] == 'USDT':
                return float(item['balance'])
    return account_value

def get_price():
    payload = {}
    path = '/openApi/swap/v2/quote/premiumIndex'
    method = "GET"
    paramsMap = {
        "symbol": symbol
    }
    paramsStr = parseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload)
    mark_price = response["data"].get("markPrice")
    return float(mark_price) if mark_price else None

def set_laverage():
    payload = {}
    path = '/openApi/swap/v2/trade/leverage'
    method = "POST"
    paramsMap = {
    "leverage": leverage,
    "side": "LONG",
    "symbol": symbol,
    "timestamp": int(time.time() * 1000)
}
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def get_open_positions():
    payload = {}
    path = '/openApi/swap/v2/user/positions'
    method = "GET"
    paramsMap = {
        "recvWindow": "0",
        "symbol": symbol,
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)

    try:
        response = send_request(method, path, paramsStr, payload)
        return len(response["data"])
    except KeyError as e:
        print(f"KeyError: {e} - 'data' key not found in the response.")
        return 2
    except Exception as e:
        print(f"An error occurred: {e}")
        return 2

def get_open_positions_margin():
    payload = {}
    path = '/openApi/swap/v2/user/positions'
    method = "GET"
    paramsMap = {
        "recvWindow": "0",
        "symbol": symbol,
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)

    try:
        response = send_request(method, path, paramsStr, payload)
        if "data" in response and len(response["data"]) > 0:
            return float(response["data"][0].get("margin", None))
        elif "data" not in response:
            raise KeyError("Key 'data' not found in the response.")
        else:
            raise ValueError("No positions found in the response.")
    except Exception as e:
        print(f"Error in get_open_positions_margin: {e}")
        raise


def order_book():
    payload = {}
    path = '/openApi/swap/v2/quote/depth'
    method = "GET"
    paramsMap = {
    "symbol": symbol,
    "limit": "5"
    }
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def set_take_profit(stop_price):
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    paramsMap = {
        "symbol": symbol,
        "side": "SELL",
        "positionSide": "LONG",
        "type": "TAKE_PROFIT_MARKET",
        "stopPrice": stop_price,
        "workingType": "MARK_PRICE",
        "closePosition": "true",
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload={})

    if response.get("code") == 0:
        return response
    else:
        print(f"Failed to set take profit: {response.get('msg', 'Unknown error')}")

def set_stop_loss(stop_price):
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    paramsMap = {
        "symbol": symbol,
        "side": "SELL",
        "positionSide": "LONG",
        "type": "STOP_MARKET",
        "stopPrice": stop_price,
        "workingType": "MARK_PRICE",
        "closePosition": "true",
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload={})

    if response.get("code") == 0:
        return response
    else:
        print(f"Failed to set stop loss: {response.get('msg', 'Unknown error')}")
        set_stop_loss(stop_price)

def open_market_position():
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    quantity = calculate_quantity(notional_value= start_notional_value, price = get_price())
    paramsMap = {
    "symbol": symbol,
    "side": "BUY",
    "positionSide": "LONG",
    "type": "MARKET",
    "quantity": quantity
}
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def open_order_limitprice(price, notional_value):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "POST"
    quantity = calculate_quantity(notional_value=notional_value, price=price)
    paramsMap = {
        "symbol": symbol,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "LIMIT",
        "price": price,
        "quantity": quantity,
        "timeInForce": "GTC",
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload)

    if response.get("code") == 0:
        return response
    else:
        print(f"Failed to open limit position: {response.get('msg', 'Unknown error')}")
        open_order_limitprice(price, notional_value)

def cancel_all_open_orders() :
    payload = {}
    path = '/openApi/swap/v2/trade/allOpenOrders'
    method = "DELETE"
    paramsMap = {
    "recvWindow": "0",
    "symbol": symbol,
    "type": "LIMIT",
    "timestamp": int(time.time() * 1000)
}
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def get_avg_open_price():
    path = '/openApi/swap/v2/user/positions'
    method = "GET"
    paramsMap = {
        "symbol": symbol,
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload={})
    if response.get("code") == 0 and response.get("data"):
        for pos in response["data"]:
            if pos["symbol"] == symbol and pos["positionSide"] == "LONG":
                return float(pos["avgPrice"])
        print(f"No position found for {symbol} with side {'LONG'}")
    else:
        return take_profit_price

def cancel_take_profit_orders():
    path = '/openApi/swap/v2/trade/openOrders'
    method = "GET"
    paramsMap = {
        "symbol": symbol,
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)
    open_orders = send_request(method, path, paramsStr, payload={})

    if open_orders.get("code") == 0 and open_orders.get("data"):
        take_profit_orders = [
            order for order in open_orders["data"]["orders"] if order["type"] == "TAKE_PROFIT_MARKET"
        ]
        for order in take_profit_orders:
            cancel_order(order["orderId"])
        return f"Cancelled {len(take_profit_orders)} Take Profit Orders for {symbol}"
    else:
        print(f"Failed to fetch open orders: {open_orders.get('msg', 'Unknown error')}")

def get_stop_loss():
    path = '/openApi/swap/v2/trade/openOrders'
    method = "GET"
    paramsMap = {
        "symbol": symbol,
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)
    open_orders = send_request(method, path, paramsStr, payload={})

    if open_orders.get("code") == 0 and open_orders.get("data"):
        stop_loss_orders = [
            order for order in open_orders["data"]["orders"] if order["type"] == "STOP_MARKET"
        ]

        if stop_loss_orders:
            return float(stop_loss_orders[0]["stopPrice"])
        else:
            return 0
    else:
        print(f"Failed to fetch open orders: {open_orders.get('msg', 'Unknown error')}")

def get_takeprofit():
    path = '/openApi/swap/v2/trade/openOrders'
    method = "GET"
    paramsMap = {
        "symbol": symbol,
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)

    try:
        open_orders = send_request(method, path, paramsStr, payload={})
        if open_orders.get("code") == 0 and open_orders.get("data"):
            take_profit_orders = [
                order for order in open_orders["data"]["orders"] if order["type"] == "TAKE_PROFIT_MARKET"
            ]
            if take_profit_orders:
                return float(take_profit_orders[0]["stopPrice"])
            else:
                return 9999999
        else:
            print(f"Failed to fetch open orders: {open_orders.get('msg', 'Unknown error')}")
            return 9999999
    except KeyError as e:
        print(f"KeyError: {e} - Key not found in the response.")
        return 9999999
    except Exception as e:
        print(f"An error occurred: {e}")
        return 9999999

def cancel_order(order_id):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    method = "DELETE"
    paramsMap = {
    "orderId": order_id,
    "symbol": symbol,
    "timestamp": int(time.time() * 1000)
}
    paramsStr = parseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def count_positions():
    margin = get_open_positions_margin()
    count = 1
    while (margin > get_balance() * 0.03) :
        margin = margin /2
        count = count + 1
    return count

def cal_frist_order_price() :
    count = count_positions()
    avg_cost = get_avg_open_price()
    if count == 1 :
        return avg_cost
    if count == 2 : 
        return #Some sensitive logic was here
    if count == 3 : 
        return #Some sensitive logic was here
    if count == 4 : 
        return #Some sensitive logic was here
    if count == 5 : 
        return #Some sensitive logic was here

def limit_orders_check():
    path = '/openApi/swap/v2/trade/openOrders'
    method = "GET"
    paramsMap = {
        "symbol": symbol,
        "timestamp": int(time.time() * 1000)
    }
    paramsStr = parseParam(paramsMap)
    open_orders = send_request(method, path, paramsStr, payload={})

    if open_orders.get("code") == 0 and open_orders.get("data"):
        limit_orders = [
            order for order in open_orders["data"]["orders"] if order["type"] == "LIMIT"
        ]
        count = count_limit_orders(orders=limit_orders)
        if count > 4 :
            cancel_all_open_orders()
            balances = get_balance()
            start_margin = get_open_positions_margin()
            start_notional_value = start_margin * leverage
            side = "BUY"
            price = #Some sensitive logic was here
            l1 = #Some sensitive logic was here
            sum_notional_value = start_notional_value
            print(sum_notional_value, #Some sensitive logic was here, price)
            while sum_notional_value + start_notional_value < #Some sensitive logic was here:
                try:
                    if sum_notional_value < #Some sensitive logic was here:
                        open_order_limitprice(price=price * l1, notional_value=start_notional_value)
                        sum_notional_value = sum_notional_value + start_notional_value
                        print(sum_notional_value, #Some sensitive logic was here, price)
                except Exception as e:
                    print(f"Error opening order: {e}")
                    break
                l1 -= 0.03
                start_notional_value *= 2

            message = "LIMIT ORDER RECOVERY"
            print(message)
            notify_status(message=message)
            time.sleep(5)
            return message

        if count == 0 and get_open_positions() == 1 and get_open_positions_margin() < get_balance()*0.30 :
            balances = get_balance()
            start_margin = get_open_positions_margin()
            start_notional_value = start_margin * leverage
            side = "BUY"
            # price = cal_frist_order_price() * #Some sensitive logic was here)
            l1 = 1 - 0.03
            sum_notional_value = start_notional_value
            # print(sum_notional_value, #Some sensitive logic was here, price)
            while sum_notional_value + start_notional_value < #Some sensitive logic was here:
                try:
                    if sum_notional_value < #Some sensitive logic was here:
                        open_order_limitprice(price=price * l1, notional_value=start_notional_value)
                        sum_notional_value = sum_notional_value + start_notional_value
                        # print(sum_notional_value, #Some sensitive logic was here, price)
                except Exception as e:
                    print(f"Error opening order: {e}")
                    break
                l1 -= 0.03
                start_notional_value *= 2

            message = "LIMIT ORDER RECOVERY"
            print(message)
            notify_status(message=message)
            time.sleep(5)
            return message

        return f"LIMIT ORDER NORMAL"
    else:
        print(f"Failed to fetch open orders: {open_orders.get('msg', 'Unknown error')}")
        return f"Failed to fetch open orders: {open_orders.get('msg', 'Unknown error')}"

def count_limit_orders(orders):
    limit_orders = [order for order in orders if order.get("type") == "LIMIT"]
    return len(limit_orders)


def open_order():
    balances = get_balance()
    # start_margin = #Some sensitive logic was here
    start_notional_value = start_margin * leverage
    time.sleep(5)
    side = "BUY"
    global stop_loss_price
    open_market_position()
    time.sleep(2)
    price = get_avg_open_price()
    #Some sensitive logic was here
    #Some sensitive logic was here
    #Some sensitive logic was here
    #Some sensitive logic was here
    #Some sensitive logic was here
    #Some sensitive logic was here
    print(f"ORDER CREATED : {price}")
    notify_order(message = f"ORDER CREATED : {round(price,int_round)}")
    #Some sensitive logic was here
    #Some sensitive logic was here
    #Some sensitive logic was here
    #Some sensitive logic was here
    manage_takeprofit()
    return f"ORDER CREATED : {price}"

def manage_takeprofit():
    global take_profit_price
    avgPrice = get_avg_open_price()
    # if avgPrice < #Some sensitive logic was here
        cancel_take_profit_orders()
        # new_take_profit_price = round(#Some sensitive logic was here, int_round)
        set_take_profit(stop_price = new_take_profit_price)
        take_profit_price = new_take_profit_price
        message = f"TAKE PROFIT PRICE : {round(new_take_profit_price,int_round)}"
        print(message)
        notify_order(message = message)

def emergency_check():
    """
    Check the current price of a symbol and compare it with the global stop_loss_price.
    If the current price is less than or equal to stop_loss_price, pause the program for 3 days.
    """
    global stop_loss_price, symbol
    try:
        current_price = get_price()
        if current_price <= stop_loss_price:
            resume_time = datetime.now() + timedelta(days=3)
            message = f"Price is below or equal to stop_loss_price. Pausing for 3 days until {resume_time.strftime('%Y-%m-%d %H:%M:%S')}."
            time.sleep(3 * 24 * 60 * 60)

    except Exception as e:
        print(f"Error: {e}")
        emergency_check()



if __name__ == '__main__':
    error_count = 0
    while True:
        try:
            open_positions = get_open_positions() + get_open_positions() + get_open_positions()
            take_profit_price = get_takeprofit()
            # emergency_check()
            if open_positions == 0:
                time.sleep(10)
                open_positions = get_open_positions() + get_open_positions() + get_open_positions()
                if open_positions == 0:
                    cancel_all_open_orders()
                    take_profit_price = 999999
                    open_order()
                    # notify(message=f"Stop loss price: {stop_loss_price}")

            if open_positions == 3:
                # stop_loss_price = get_stop_loss()
                manage_takeprofit()
                limit_orders_check()

            thai_time = datetime.utcnow() + timedelta(hours=7)

            if thai_time.minute % 15 == 0:
                message = f"{thai_time.strftime('%H:%M')} Status : Running"
                notify_status(message=message)
                time.sleep(60)

            print(f"{thai_time.strftime('%Y-%m-%d %H:%M')} Status : {open_positions}")
            time.sleep(1)
            error_count = 0

        except Exception as e:
            error_count += 1
            print(f"Error occurred: {e}")
            time.sleep(2)
            if error_count >= 10:
                notify_status(message=f"Error occurred 10 consecutive times !!!")
                error_count = 0