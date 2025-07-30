import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import time

# Page configuration
st.set_page_config(
    page_title="USC Stock Price Tracker",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(90deg, #990000 0%, #FFC72C 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin: 20px 0;
    }
    
    .logo-text {
        font-size: 18px;
        font-weight: bold;
        color: #FFC72C;
    }
    
    .stock-input-section {
        background: #262626;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #FFC72C;
        margin-bottom: 20px;
    }
    
    .metrics-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #444;
        margin: 15px 0;
    }
    
    .chart-container {
        background: #1a1a1a;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        margin: 20px 0;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(90deg, #990000 0%, #FFC72C 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 199, 44, 0.3);
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: #262626;
        border: 1px solid #FFC72C;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(255, 199, 44, 0.1);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background: #333;
        color: white;
        border: 2px solid #FFC72C;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Footer styling */
    .footer {
        background: #262626;
        padding: 15px;
        border-radius: 10px;
        border-top: 3px solid #FFC72C;
        margin-top: 30px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header with logos
st.markdown("""
<div class="main-header">
    <h1>🇺🇸 USC Stock Price Tracker 🏛️</h1>
    <div class="logo-container">
        <div>
            <span style="font-size: 48px;">🇺🇸</span>
            <div class="logo-text">United States</div>
        </div>
        <div style="font-size: 40px; color: #FFC72C;">⚡</div>
        <div>
            <span style="font-size: 48px;">🏛️</span>
            <div class="logo-text">USC Trojans</div>
        </div>
    </div>
    <p style="margin: 10px 0; font-size: 18px;">Professional Stock Market Analysis Platform</p>
</div>
""", unsafe_allow_html=True)

# Get API key from environment variables
API_KEY = os.getenv("TWELVE_DATA_API_KEY", "demo")


def validate_stock_symbol(symbol):
    """Validate stock symbol format"""
    if not symbol:
        return False, "Please enter a stock symbol"

    if not symbol.replace(".", "").isalnum():
        return False, "Stock symbol should only contain letters, numbers, and periods"

    if len(symbol) > 10:
        return False, "Stock symbol should be 10 characters or less"

    return True, ""


def fetch_stock_data(symbol, interval="1day", outputsize=7):
    """Fetch stock data from Twelve Data API"""
    try:
        # API endpoint for time series data
        url = "https://api.twelvedata.com/time_series"

        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "outputsize": outputsize,
            "apikey": API_KEY
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Check for API errors
            if "status" in data and data["status"] == "error":
                return None, data.get("message", "Unknown API error")

            if "values" not in data:
                return None, "No data available for this symbol"

            return data, None
        else:
            return None, f"API request failed with status code: {response.status_code}"

    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def get_current_price(symbol):
    """Fetch current stock price"""
    try:
        url = "https://api.twelvedata.com/price"
        params = {"symbol": symbol.upper(), "apikey": API_KEY}

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if "status" in data and data["status"] == "error":
                return None, data.get("message", "Unknown API error")

            if "price" in data:
                return float(data["price"]), None
            else:
                return None, "Price data not available"
        else:
            return None, f"API request failed with status code: {response.status_code}"

    except Exception as e:
        return None, f"Error fetching current price: {str(e)}"


def create_price_chart(df, symbol):
    """Create interactive price chart using Plotly"""
    fig = go.Figure()

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(x=df['datetime'],
                       open=df['open'],
                       high=df['high'],
                       low=df['low'],
                       close=df['close'],
                       name=symbol.upper()))

    # Update layout with dark theme
    fig.update_layout(
        title=f"🇺🇸 {symbol.upper()} - 7-Day Price Chart 🏛️",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        height=500,
        showlegend=False,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='#ffffff', family='monospace'),
        title_font=dict(size=20, color='#FFC72C')
    )

    # Format x-axis
    fig.update_xaxes(tickformat="%m/%d", tickmode="linear", dtick="D1")

    return fig


def process_stock_data(data):
    """Process API response into DataFrame"""
    try:
        values = data["values"]

        # Convert to DataFrame
        df = pd.DataFrame(values)

        # Convert data types
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        df['volume'] = pd.to_numeric(df['volume'])

        # Sort by date (oldest first)
        df = df.sort_values('datetime')

        return df, None

    except Exception as e:
        return None, f"Error processing data: {str(e)}"


# Main interface with enhanced styling
st.markdown('<div class="stock-input-section">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 📊 Enter Stock Symbol")
    # Stock symbol input
    stock_symbol = st.text_input(
        "Stock Symbol",
        placeholder="e.g., AAPL, GOOGL, TSLA",
        help="Enter a valid stock symbol",
        label_visibility="collapsed"
    ).strip().upper()
    
    # Search button
    search_clicked = st.button("🚀 Analyze Stock", type="primary")
    
    st.markdown("---")
    st.markdown("**Popular Stocks:**")
    st.markdown("• AAPL - Apple Inc.")
    st.markdown("• GOOGL - Alphabet Inc.")
    st.markdown("• TSLA - Tesla Inc.")
    st.markdown("• MSFT - Microsoft Corp.")
    st.markdown("• AMZN - Amazon.com Inc.")

st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if search_clicked and stock_symbol:
        # Validate input
        is_valid, error_msg = validate_stock_symbol(stock_symbol)

        if not is_valid:
            st.error(error_msg)
        else:
            # Show loading spinner
            with st.spinner(f"Fetching data for {stock_symbol}..."):
                # Fetch current price
                current_price, price_error = get_current_price(stock_symbol)

                # Fetch historical data
                stock_data, data_error = fetch_stock_data(stock_symbol)

                if data_error:
                    st.error(f"Error fetching stock data: {data_error}")
                elif stock_data:
                    # Process the data
                    df, process_error = process_stock_data(stock_data)

                    if process_error:
                        st.error(process_error)
                    else:
                        # Display current price with enhanced styling
                        st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
                        
                        if current_price and not price_error:
                            st.metric(
                                label=f"💰 {stock_symbol} Current Price",
                                value=f"${current_price:.2f}",
                                delta=None
                            )
                        else:
                            st.warning("⚠️ Current price not available")

                        # Display basic information with enhanced metrics
                        st.markdown("### 📈 Key Metrics")
                        col_info1, col_info2, col_info3 = st.columns(3)

                        with col_info1:
                            latest_close = df['close'].iloc[-1]
                            st.metric("🔹 Latest Close", f"${latest_close:.2f}")

                        with col_info2:
                            week_high = df['high'].max()
                            st.metric("📊 7-Day High", f"${week_high:.2f}")

                        with col_info3:
                            week_low = df['low'].min()
                            st.metric("📉 7-Day Low", f"${week_low:.2f}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Create and display chart with enhanced container
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        st.markdown("### 📊 Interactive Price Chart")
                        fig = create_price_chart(df, stock_symbol)
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Display data table
                        with st.expander("View Raw Data"):
                            # Format the dataframe for display
                            display_df = df.copy()
                            display_df['datetime'] = display_df[
                                'datetime'].dt.strftime('%Y-%m-%d')
                            display_df = display_df[[
                                'datetime', 'open', 'high', 'low', 'close',
                                'volume'
                            ]]
                            display_df.columns = [
                                'Date', 'Open', 'High', 'Low', 'Close',
                                'Volume'
                            ]

                            # Format numeric columns
                            for col in ['Open', 'High', 'Low', 'Close']:
                                display_df[col] = display_df[col].apply(
                                    lambda x: f"${x:.2f}")

                            display_df['Volume'] = display_df['Volume'].apply(
                                lambda x: f"{x:,}")

                            st.dataframe(display_df, use_container_width=True)

    elif search_clicked:
        st.warning("Please enter a stock symbol")

# Enhanced Footer with USC branding
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center;">
        <h3>🇺🇸 USC Financial Analysis Platform 🏛️</h3>
        <div style="display: flex; justify-content: space-around; margin: 20px 0;">
            <div>
                <strong>📊 Data Source:</strong> Twelve Data API<br>
                <strong>📈 Chart Type:</strong> Candlestick (OHLC)<br>
                <strong>⏰ Time Period:</strong> 7 days
            </div>
            <div>
                <span style="font-size: 24px;">🇺🇸</span><br>
                <strong>United States</strong><br>
                Financial Markets
            </div>
            <div>
                <span style="font-size: 24px;">🏛️</span><br>
                <strong>USC Trojans</strong><br>
                Fight On!
            </div>
        </div>
        <p><em>Note: This application uses real-time stock data. Market data may be delayed.</em></p>
        <p style="color: #FFC72C; font-weight: bold;">Developed for University of Southern California</p>
    </div>
""", unsafe_allow_html=True)

# API key status with enhanced styling
if API_KEY == "demo":
    st.info("ℹ️ Using demo API key. For production use, set TWELVE_DATA_API_KEY environment variable.")

st.markdown('</div>', unsafe_allow_html=True)
