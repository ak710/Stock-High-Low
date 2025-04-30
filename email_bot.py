# Import required libraries
# Import required libraries
import json
import yfinance as yf
import schedule
import time
import smtplib
from email.message import EmailMessage

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

def send_email_alert(subject, body, to_email):
    # Email account credentials
    sender_email = "stockalert@zohomailcloud.ca"
    sender_password = "Akshatronit1!"  # Consider using environment variables for security

    # Compose the email
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    # Connect to Gmail SMTP server (or your provider's SMTP)
    with smtplib.SMTP('smtp.zohocloud.ca', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

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
                    subject = f"Stock Alert: {stock['ticker']}"
                    send_email_alert(subject, message, "akshatk710@gmail.com")
                    updated = True
                    
            except Exception as e:
                print(f"Error processing {stock['ticker']}: {str(e)}")
        
        if updated:
            save_stock_data('ticker_data.json', stock_data)
            print("Successfully updated thresholds")
            
    except Exception as e:
        print(f"Monitoring error: {str(e)}")

# Schedule the job every 10 minutes
schedule.every(10).minutes.do(stock_monitor)

# Run continuously
while True:
    schedule.run_pending()
    time.sleep(1)





