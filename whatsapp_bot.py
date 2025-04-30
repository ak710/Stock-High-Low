# Import required libraries
# Import required libraries
import json
import yfinance as yf
from twilio.rest import Client
import schedule
import time

def load_stock_data(file_path):
    with open(file_path) as f:
        return [json.loads(line) for line in f]

def save_stock_data(file_path, data):
    with open(file_path, 'w') as f:
        for stock in data:
            json_line = json.dumps(stock)
            f.write(json_line + '\n')

def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.info
    return data.get('regularMarketPrice', data.get('currentPrice'))

def check_and_update_thresholds(stock, current_price):
    alerts = []
    periods = [
        ('52 Week', '52_week_high', '52_week_low'),
        ('6 Month', '6_month_high', '6_month_low'),
        ('1 Month', '1_month_high', '1_month_low')
    ]
    
    for name, high_key, low_key in periods:
        period_high = stock[high_key]
        period_low = stock[low_key]
        
        if current_price > period_high:
            alerts.append(f"ABOVE {name} High ({period_high:.2f})")
            stock[high_key] = current_price  # Update historical high
        elif current_price < period_low:
            alerts.append(f"BELOW {name} Low ({period_low:.2f})")
            stock[low_key] = current_price  # Update historical low
    
    return alerts

def send_whatsapp_alert(message):
    account_sid = 'AC0644ffe8ece43eac62e00d964c9a5680'
    auth_token = 'bd209dca4360e7d3cf7cf6379e890274'
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio sandbox number
        body=message,
        to='whatsapp:+16043688457'  # Your verified number
    )

def stock_monitor():
    try:
        stock_data = load_stock_data('ticker_data.json')
        updated = False
        
        for stock in stock_data:
            try:
                current_price = get_current_price(stock['ticker'])
                if current_price is None:
                    continue
                
                alerts = check_and_update_thresholds(stock, current_price)
                
                if alerts:
                    message = (f"ALERT: {stock['ticker']} at {current_price:.2f}\n" 
                              + "\n".join(alerts))
                    send_whatsapp_alert(message)
                    updated = True
                    
            except Exception as e:
                print(f"Error processing {stock['ticker']}: {str(e)}")
        
        if updated:
            save_stock_data('ticker_data.json', stock_data)
            print("Successfully updated thresholds")
            
    except Exception as e:
        print(f"Monitoring error: {str(e)}")

# Schedule the job every 10 minutes
schedule.every(0.1).minutes.do(stock_monitor)

# Run continuously
while True:
    schedule.run_pending()
    time.sleep(1)





