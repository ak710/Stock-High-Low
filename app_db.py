import streamlit as st
import yfinance as yf
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import os
from pyairtable import Api

AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_NAME = st.secrets["AIRTABLE_TABLE_NAME"]

def get_airtable_table():
    api = Api(AIRTABLE_TOKEN)
    return api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

def save_to_airtable(data):
    table = get_airtable_table()
    table.create(data)

def load_from_airtable():
    table = get_airtable_table()
    records = table.all()
    # Convert Airtable records to your expected format
    return [rec['fields'] for rec in records]

def delete_from_airtable(ticker):
    table = get_airtable_table()
    # Find record by ticker and delete
    for rec in table.all():
        if rec['fields'].get('ticker', '').upper() == ticker.upper():
            table.delete(rec['id'])
            break

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



# Streamlit UI
st.title("Stock Ticker Tracker with Historical Ranges")

saved_data = load_from_airtable()
new_ticker = st.text_input("Enter stock ticker:", "AAPL").strip().upper()

if st.button("Add Ticker"):
    if not new_ticker:
        st.warning("Please enter a ticker")
    elif is_duplicate_ticker(new_ticker, saved_data):
        st.warning(f"{new_ticker} is already in your list!")
    elif validate_ticker(new_ticker):
        price_data = get_price_ranges(new_ticker)
        if price_data:
            save_to_airtable(price_data)
            st.success(f"Saved {new_ticker} with price ranges!")
            st.rerun()
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
            delete_from_airtable(item['ticker'])
            st.success(f"Deleted {item['ticker']}")
            st.rerun()

else:
    st.info("No tickers saved yet")