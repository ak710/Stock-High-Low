import streamlit as st
import yfinance as yf
import json
import os
import pandas as pd
from datetime import datetime, timedelta


DATA_FILE = "ticker_data.json"
# Check if the text file exists, if not create it

def is_duplicate_ticker(ticker, saved_data):
    return any(item['ticker'].upper() == ticker.upper() for item in saved_data)

def validate_ticker(ticker):
    """Check if ticker exists using recent price data"""
    try:
        data = yf.Ticker(ticker).history(period="7d")
        return not data.empty
    except:
        return False

def get_price_ranges(ticker):
    """Get historical price ranges using yfinance"""
    stock = yf.Ticker(ticker)
    
    try:
        
        # Get 52-week ranges from stock info
        fifty_two_week_high = stock.info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = stock.info.get('fiftyTwoWeekLow')
        
        # Calculate 6-month and 1-month ranges
        six_month = stock.history(period="6mo")
        one_month = stock.history(period="1mo")
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            '52_week_high': fifty_two_week_high,
            '52_week_low': fifty_two_week_low,
            '6_month_high': six_month['High'].max(),
            '6_month_low': six_month['Low'].min(),
            '1_month_high': one_month['High'].max(),
            '1_month_low': one_month['Low'].min()
        }
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def save_to_file(data):
    """Append data to JSON file"""
    with open(DATA_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

def load_from_file():
    """Load all ticker data from JSON file"""
    try:
        with open(DATA_FILE, "r") as f:
            return [json.loads(line) for line in f]
    except FileNotFoundError:
        return []
    
def save_all(data):
        with open(DATA_FILE, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")


# Streamlit UI
st.title("Stock Ticker Tracker with Historical Ranges")

saved_data = load_from_file()
new_ticker = st.text_input("Enter stock ticker:", "AAPL").strip().upper()

if st.button("Add Ticker"):
    if not new_ticker:
        st.warning("Please enter a ticker")
    elif is_duplicate_ticker(new_ticker, saved_data):
        st.warning(f"{new_ticker} is already in your list!")
    elif validate_ticker(new_ticker):
        price_data = get_price_ranges(new_ticker)
        if price_data:
            save_to_file(price_data)
            st.success(f"Saved {new_ticker} with price ranges!")
            st.rerun()  # Refresh to show the new ticker
    else:
        st.error("Invalid ticker symbol")

# Display saved data
if saved_data:
    st.subheader("Saved Tickers with Price Ranges")
    
    # Create table headers
    headers = ["Ticker", "Current Price","52W High", "52W Low", "6M High", "6M Low", "1M High", "1M Low", "Delete"]
    col_widths = [2,2,2,2,2,2,2,2,3]
    header_cols = st.columns(col_widths)
    for col, header in zip(header_cols, headers):
        col.write(f"**{header}**")

    for idx, item in enumerate(saved_data):
        Current_price = yf.Ticker(item['ticker']).fast_info["last_price"]
        cols = st.columns(col_widths)
        cols[0].write(item['ticker'])
        cols[1].markdown(f":green[${Current_price:.2f}]")
        cols[2].write(f"${item['52_week_high']:.2f}")
        cols[3].write(f"${item['52_week_low']:.2f}")
        cols[4].write(f"${item['6_month_high']:.2f}")
        cols[5].write(f"${item['6_month_low']:.2f}")
        cols[6].write(f"${item['1_month_high']:.2f}")
        cols[7].write(f"${item['1_month_low']:.2f}")
        if cols[8].button("Delete", key=f"delete_{item['ticker']}_{idx}"):
            saved_data.remove(item)
            save_all(saved_data)
            st.success(f"Deleted {item['ticker']}")
            st.rerun()

else:
    st.info("No tickers saved yet")