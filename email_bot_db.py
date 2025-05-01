# Import required libraries
# Import required libraries
import json
import yfinance as yf
import schedule
import time
import smtplib
from email.message import EmailMessage
import requests
import os

AIRTABLE_TOKEN = "patNEKm0aXuQ8djrb.0444341226d0539c89e8d55e0ab4a181410446dd1d2bf4b5b2d9131ace6061e2"
AIRTABLE_BASE_ID = "appjnZkgUkiB12Dq3"
AIRTABLE_TABLE_NAME = "tbl92uPxxsNE8PHUA"

AIRTABLE_ENDPOINT = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
AIRTABLE_HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

def get_all_stocks():
    """Fetch all stock records from Airtable."""
    response = requests.get(AIRTABLE_ENDPOINT, headers=AIRTABLE_HEADERS)
    response.raise_for_status()
    records = response.json().get("records", [])
    # Return a list of dicts: [{...fields..., "id": record_id}, ...]
    return [{"id": rec["id"], **rec["fields"]} for rec in records]

def update_stock_record(record_id, fields):
    """Update Airtable record using its internal record ID (REQUIRED)"""
    url = f"{AIRTABLE_ENDPOINT}/{record_id}"
    data = {"fields": fields, "typecast": True}  # Critical for data type conversion
    response = requests.patch(url, json=data, headers=AIRTABLE_HEADERS)
    try:
        response.raise_for_status()
        print(f"Updated {record_id}: {fields}")  # Debug log
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"API Error: {e.response.text}")  # Show Airtable's error message
        return None

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
        elif current_price < period_low:
            alerts.append(f"BELOW {name} Low ({period_low:.2f})")
    
    return alerts

def send_email_alert(subject, body, to_email):
    # Email account credentials
    sender_email = "stockbotalerter@gmail.com"
    sender_password = "gxso omri zxvl ikhe"  # Consider using environment variables for security

    # Compose the email
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    # Connect to Gmail SMTP server (or your provider's SMTP)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

def stock_monitor():
    try:
        stock_data = get_all_stocks()
        updated = False
        for stock in stock_data:
            try:
                ticker = stock['ticker']
                current_price = get_current_price(ticker)
                if current_price is None:
                    continue

                alerts = check_and_update_thresholds(stock, current_price)
                update_fields = {}

                # If a new high/low is set, update the relevant field(s)
                periods = [
                    ('52 Week', '52_week_high', '52_week_low'),
                    ('6 Month', '6_month_high', '6_month_low'),
                    ('1 Month', '1_month_high', '1_month_low')
                ]
                for name, high_key, low_key in periods:
                    period_high = stock.get(high_key)
                    period_low = stock.get(low_key)
                    if current_price > period_high:
                        print("current price is greater than period high")
                        update_fields[high_key] = current_price
                    elif current_price < period_low:
                        print("current price is less than period low")
                        update_fields[low_key] = current_price
                
                print(update_fields)
                if alerts:
                    print("sending email")
                    message = (f"ALERT: {ticker} at {current_price:.2f}\n"
                               + "\n".join(alerts))
                    subject = f"Stock Alert: {ticker}"
                    send_email_alert(subject, message, "akshatk710@gmail.com")
                    updated = True

                # Update Airtable if any field changed
                if update_fields:
                    print(f"Updating {stock['id']} with {update_fields}")
                    update_stock_record(stock['id'], update_fields)

            except Exception as e:
                print(f"Error processing {stock.get('ticker', 'unknown')}: {str(e)}")

        if updated:
            print("Successfully updated thresholds")

    except Exception as e:
        print(f"Monitoring error: {str(e)}")

# Schedule the job every 10 minutes
schedule.every(10).minutes.do(stock_monitor)

# Run continuously
while True:
    schedule.run_pending()
    time.sleep(1)





