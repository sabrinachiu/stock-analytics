import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="MarketInsight Pro | Real-Time Stock Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a premium look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔍 Stock Search")
ticker_symbol = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL").upper()

st.sidebar.subheader("📅 Date Range")
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
date_range = st.sidebar.date_input("Select Range", [start_date, end_date])

# Main Header
st.title("📈 MarketInsight Pro")
st.markdown(f"### Real-time analysis for **{ticker_symbol}**")

@st.cache_data(ttl=3600)
def get_stock_data(ticker, start, end):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start, end=end)
        info = stock.info
        return df, info
    except Exception as e:
        return None, None

if ticker_symbol:
    if len(date_range) == 2:
        df, info = get_stock_data(ticker_symbol, date_range[0], date_range[1])
        
        if df is not None and not df.empty:
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            latest_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2] if len(df) > 1 else latest_price
            price_diff = latest_price - prev_price
            pct_change = (price_diff / prev_price) * 100
            
            col1.metric("Current Price", f"${latest_price:.2f}", f"{pct_change:.2f}%")
            col2.metric("Day High", f"${df['High'].iloc[-1]:.2f}")
            col3.metric("Day Low", f"${df['Low'].iloc[-1]:.2f}")
            col4.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")

            # Chart Section
            st.divider()
            st.subheader("Interactive Price Chart")
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ))
            
            fig.update_layout(
                template='plotly_white',
                xaxis_rangeslider_visible=False,
                height=500,
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Details Tabs
            tab1, tab2, tab3 = st.tabs(["📊 Key Statistics", "🏢 Company Info", "📜 Raw Data"])
            
            with tab1:
                st.subheader("Fundamental Metrics")
                stats_cols = st.columns(3)
                
                with stats_cols[0]:
                    st.write(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")
                    st.write(f"**Trailing P/E:** {info.get('trailingPE', 'N/A')}")
                    st.write(f"**Forward P/E:** {info.get('forwardPE', 'N/A')}")
                
                with stats_cols[1]:
                    st.write(f"**Dividend Yield:** {info.get('dividendYield', 'N/A')}")
                    st.write(f"**52 Week High:** {info.get('fiftyTwoWeekHigh', 'N/A')}")
                    st.write(f"**52 Week Low:** {info.get('fiftyTwoWeekLow', 'N/A')}")
                
                with stats_cols[2]:
                    st.write(f"**Revenue:** {info.get('totalRevenue', 'N/A'):,}")
                    st.write(f"**PEG Ratio:** {info.get('pegRatio', 'N/A')}")
                    st.write(f"**Price to Book:** {info.get('priceToBook', 'N/A')}")

            with tab2:
                st.subheader(info.get('longName', ticker_symbol))
                st.write(info.get('longBusinessSummary', "No summary available."))
                st.markdown(f"**Website:** [{info.get('website', '')}]({info.get('website', '')})")
                st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")

            with tab3:
                st.subheader("Historical Pricing Data")
                st.dataframe(df.sort_index(ascending=False), use_container_width=True)

        else:
            st.error(f"Could not find data for ticker: {ticker_symbol}. Please check the symbol and try again.")
    else:
        st.info("Please select a valid date range in the sidebar.")
else:
    st.warning("Please enter a ticker symbol in the sidebar.")

# Footer
st.divider()
st.caption("Powered by MarketInsight Pro | Data from Yahoo! Finance via yfinance")
