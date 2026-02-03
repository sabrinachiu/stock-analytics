import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="SkyStock Analytics | Premium Market Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Modern Light Mode Friendly CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #f8fafc;
    }

    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }

    div[data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: white;
        padding: 10px 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 6px;
        color: #64748b;
    }

    .stTabs [aria-selected="true"] {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #ffffff;
    }

    h1, h2, h3, h4 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to format large numbers safely
def format_val(val, format_type="num"):
    if val is None or val == 'N/A' or val == '':
        return "N/A"
    
    try:
        if format_type == "curr":
            return f"${val:,.2f}"
        elif format_type == "pct":
            return f"{val*100:.2f}%"
        elif format_type == "large":
            if val >= 1_000_000_000_000: return f"{val / 1_000_000_000_000:.2f}T"
            if val >= 1_000_000_000: return f"{val / 1_000_000_000:.2f}B"
            if val >= 1_000_000: return f"{val / 1_000_000:.2f}M"
            return f"{val:,}"
        else:
            return f"{val:,}"
    except:
        return str(val)

# Sidebar
with st.sidebar:
    st.markdown("# 💎")
    st.title("SkyStock Pro")
    st.markdown("---")
    ticker_symbol = st.text_input("🔍 Search Ticker", value="NVDA").upper()
    
    selected_period = st.selectbox(
        "Time Range", 
        ["1 Month", "6 Months", "1 Year", "2 Years", "5 Years"], 
        index=2
    )
    period_map = {"1 Month": 30, "6 Months": 180, "1 Year": 365, "2 Years": 730, "5 Years": 1825}
    
    st.markdown("---")
    st.subheader("Chart Options")
    show_ma20 = st.checkbox("20D Moving Avg", value=True)
    show_ma50 = st.checkbox("50D Moving Avg", value=True)

@st.cache_data(ttl=600)
def fetch_data(ticker, days):
    try:
        stock = yf.Ticker(ticker)
        end = datetime.now()
        start = end - timedelta(days=days)
        df = stock.history(start=start, end=end)
        info = stock.info
        return df, info
    except:
        return None, None

if ticker_symbol:
    df, info = fetch_data(ticker_symbol, period_map[selected_period])
    
    if df is not None and not df.empty:
        # Header
        col_logo, col_title = st.columns([0.07, 0.93])
        with col_logo:
            st.markdown("## 📈")
        with col_title:
            st.title(f"{info.get('longName', ticker_symbol)}")

        # Fast Stats
        m1, m2, m3, m4 = st.columns(4)
        latest_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else latest_price
        change = latest_price - prev_price
        pct_change = (change / prev_price) * 100
        
        m1.metric("Current Price", f"${latest_price:.2f}", f"{pct_change:.2f}%")
        m2.metric("Day High", f"${df['High'].iloc[-1]:.2f}")
        m3.metric("Market Cap", format_val(info.get('marketCap'), "large"))
        m4.metric("Forward PE", format_val(info.get('forwardPE')))

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'
        ))
        
        if show_ma20:
            df['MA20'] = df['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#38bdf8', width=1.5), name='MA20'))
        if show_ma50:
            df['MA50'] = df['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='#f43f5e', width=1.5), name='MA50'))

        fig.update_layout(
            template='plotly_white',
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabs
        tab1, tab2, tab3 = st.tabs(["Company Info", "Valuation", "History"])
        
        with tab1:
            st.subheader("Business Summary")
            st.write(info.get('longBusinessSummary', "No summary available."))
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            with c2:
                # FIXED: Added helper function to prevent error when value is missing
                st.write(f"**Employees:** {format_val(info.get('fullTimeEmployees'))}")
                st.write(f"**Location:** {info.get('city', 'N/A')}, {info.get('country', 'N/A')}")
            with c3:
                st.write(f"**Website:** [Visit]({info.get('website', '#')})")
                st.write(f"**Exchange:** {info.get('exchange', 'N/A')}")

        with tab2:
            st.subheader("Financial Metrics")
            vcol1, vcol2 = st.columns(2)
            with vcol1:
                st.markdown("**Valuation**")
                st.write(f"**Trailing PE:** {format_val(info.get('trailingPE'))}")
                st.write(f"**Price to Book:** {format_val(info.get('priceToBook'))}")
                st.write(f"**EV/EBITDA:** {format_val(info.get('enterpriseToEbitda'))}")
            with vcol2:
                st.markdown("**Performance**")
                st.write(f"**52W High:** {format_val(info.get('fiftyTwoWeekHigh'), 'curr')}")
                st.write(f"**52W Low:** {format_val(info.get('fiftyTwoWeekLow'), 'curr')}")
                st.write(f"**Div. Yield:** {format_val(info.get('dividendYield'), 'pct')}")

        with tab3:
            st.subheader("Historical Pricing")
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)

    else:
        st.error("⚠️ Ticker not found. Please try another symbol (e.g. AAPL, QQQ, TSLA).")

st.markdown("---")
st.caption("Powered by SkyStock Pro | Finance Data Engine v1.3")
