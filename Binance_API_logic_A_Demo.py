from binance.client import Client
import math
import time
from datetime import datetime, timedelta
import os
import requests

api_key = #Some sensitive logic was here
api_secret = #Some sensitive logic was here

leverage = #Some sensitive logic was here
portfolio_value = #Some sensitive logic was here
start_amount = #Some sensitive logic was here
symbol = #Some sensitive logic was here
take_profit_price = #Some sensitive logic was here
stop_loss_price = #Some sensitive logic was here
round_quantity = #Some sensitive logic was here
round_price = #Some sensitive logic was here

client = Client(api_key, api_secret, testnet=True)  

def notify(message):
    bot_token = #Some sensitive logic was here
    chat_id = #Some sensitive logic was here
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=payload)

def get_futures_balance():
    try:
        futures_balance = client.futures_account_balance()
        
        print("Futures Account balance :")
        for asset in futures_balance:
            if float(asset["balance"]) > 0:
                print(f"Asset: {asset['asset']}, Balance: {asset['balance']}")
    except Exception as e:
        print(f"error: {e}")
        
def open_order():
    side = "BUY"
    global stop_loss_price
    try:
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        
        ticker = client.futures_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])
        quantity = round(start_amount / price, round_quantity)
        
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity = quantity
        )
        # Create LIMIT orders at different price levels
        #Some sensitive logic was here
        #Some sensitive logic was here
        #Some sensitive logic was here
        #Some sensitive logic was here
        #Some sensitive logic was here
        #Some sensitive logic was here
        #Some sensitive logic was here
        print("Market Order created successfully")
        notify(message = "Order created successfully")
        
    except Exception as e:
        notify(message = f"Error: {e}")
   
def open_order_limitprice(price, notional_value):
    side = "BUY"
    order_type = "LIMIT"
    price = round(price, round_price)
    try:
        quantity = round(notional_value / price, round_quantity)
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            price=price,
            timeInForce="GTC"
        )

        print("LIMIT Order created successfully: " + str(price))
        
    except Exception as e:
        notify(message = f"Error: {e}")

def check_open_positions():
    try:
        positions = client.futures_position_information()
        open_positions = [position for position in positions if float(position['positionAmt']) != 0]
        return len(open_positions)

    except Exception as e:
        print(f"Error: {e}")
        return 1
    
def cancel_all_orders():
    try:
        response = client.futures_cancel_all_open_orders(symbol=symbol)
        print(f"All open orders for {symbol} have been canceled.")
        return response
    
    except Exception as e:
        notify(message = f"Error: {e}")
        return None
        
def manage_takeprofit():
    try:
        global take_profit_price
        positions = client.futures_position_information()
        for position in positions:
            if float(position['positionAmt']) > 0:
                entry_price = float(position['entryPrice'])
                position_amt = float(position['positionAmt'])
                quantity = abs(position_amt)

                if entry_price < #Some sensitive logic was here
                    cancel_take_profit_orders()
                    new_take_profit_price = round(#Some sensitive logic was here, round_price)
                    order = client.futures_create_order(
                        symbol=position['symbol'],
                        side="SELL",
                        type="TAKE_PROFIT_MARKET",
                        stopPrice=new_take_profit_price,
                        closePosition=True,
                        timeInForce="GTC"
                    )
                    notify(message=f"take profit price: {new_take_profit_price}")
                    take_profit_price = new_take_profit_price
    except Exception as e:
        notify(message = f"Error: {e}")

def set_stop_loss(stop_loss_price):
    try:
        trigger_type="MARK_PRICE"
        stop_loss_price = round(stop_loss_price, round_price)
        order = client.futures_create_order(
            symbol=symbol,
            side="SELL", 
            type="STOP_MARKET",
            stopPrice=stop_loss_price,
            closePosition=True,
            timeInForce="GTE_GTC",
            workingType=trigger_type
        )
    except Exception as e:
        print(f"Error: {e}")

def emergency_check():
    global stop_loss_price, symbol
    try:
        ticker = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        if current_price <= stop_loss_price:
            resume_time = datetime.now() + timedelta(days=3)
            notify(message = f"Price is below or equal to stop_loss_price. Pausing for 3 days until {resume_time.strftime('%Y-%m-%d %H:%M:%S')}.")
            time.sleep(3 * 24 * 60 * 60)

    except Exception as e:
        print(f"Error: {e}")
        
def get_stop_loss():
    try:
        open_orders = client.futures_get_open_orders(symbol=symbol)
        for order in open_orders:
            if order['type'] == 'STOP_MARKET': 
                stop_loss_price = order['stopPrice']
                return float(stop_loss_price)
        
        print(f"No Stop Loss found for {symbol}.")
        return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def cancel_take_profit_orders():
    try:
        open_orders = client.futures_get_open_orders(symbol=symbol)
        
        for order in open_orders:
            if order['type'] == 'TAKE_PROFIT_MARKET': 
                order_id = order['orderId']
                client.futures_cancel_order(symbol=symbol, orderId=order_id)
    except Exception as e:
        print(f"Error: {e}")


while True:
    open_positions = check_open_positions()  
    if open_positions == 0:
        cancel_all_orders()
        take_profit_price = #Some sensitive logic was here
        open_order()
        notify(message=f"stop loss price: {stop_loss_price}")
            
    if open_positions > 0:
        manage_takeprofit()
        stop_loss_price = get_stop_loss()
        emergency_check()