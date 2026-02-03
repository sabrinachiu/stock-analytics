import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="SkyStock Analytics | Premium Market Intelligence",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    .stApp {
        background: transparent;
    }

    /* Glassmorphism card */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.2);
    }

    /* Style Streamlit components */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }

    div[data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #94a3b8;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(56, 189, 248, 0.1) !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }

    h1, h2, h3 {
        color: #f8fafc !important;
        letter-spacing: -0.025em;
    }

    .sidebar .sidebar-content {
        background-image: linear-gradient(#1e293b,#0f172a);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to format numbers
def format_large_number(num):
    if num is None or num == 'N/A':
        return "N/A"
    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    else:
        return f"{num:,}"

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/diamond.png", width=80)
    st.title("SkyStock Pro")
    st.markdown("---")
    ticker_symbol = st.text_input("💎 Enter Ticker Symbol", value="NVDA").upper()
    
    st.subheader("📅 Analysis Period")
    period_options = {
        "1 Month": 30,
        "6 Months": 180,
        "1 Year": 365,
        "2 Years": 730,
        "5 Years": 1825
    }
    selected_period = st.selectbox("Select Range", list(period_options.keys()), index=2)
    
    st.markdown("---")
    st.subheader("🛠 Technical Settings")
    show_ma20 = st.checkbox("Show 20-Day SMA", value=True)
    show_ma50 = st.checkbox("Show 50-Day SMA", value=True)
    
    st.markdown("---")
    st.caption("v1.2.0 | High-Precision Financial Data")

# Main Content Logic
@st.cache_data(ttl=600)
def fetch_data(ticker, days):
    try:
        stock = yf.Ticker(ticker)
        end = datetime.now()
        start = end - timedelta(days=days)
        df = stock.history(start=start, end=end)
        info = stock.info
        return df, info
    except Exception as e:
        return None, None

if ticker_symbol:
    with st.spinner(f"Synchronizing global markets for {ticker_symbol}..."):
        df, info = fetch_data(ticker_symbol, period_options[selected_period])
        
    if df is not None and not df.empty:
        # Header with Logo
        col_h1, col_h2 = st.columns([0.1, 0.9])
        with col_h1:
            logo_url = info.get('website', '').replace('http://', 'https://') + '/favicon.ico'
            st.image(f"https://www.google.com/s2/favicons?sz=64&domain={info.get('website', 'finance.yahoo.com')}", width=48)
        with col_h2:
            st.title(f"{info.get('longName', ticker_symbol)} ({ticker_symbol})")
            st.caption(f"{info.get('exchange', 'Unknown Exchange')} • {info.get('currency', 'USD')}")

        # Metrics Row
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        latest_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2] if len(df) > 1 else latest_price
        change = latest_price - prev_price
        pct_change = (change / prev_price) * 100
        
        with m_col1:
            st.metric("Price", f"${latest_price:.2f}", f"{pct_change:.2f}%")
        with m_col2:
            st.metric("Day High", f"${df['High'].iloc[-1]:.2f}")
        with m_col3:
            st.metric("Market Cap", format_large_number(info.get('marketCap')))
        with m_col4:
            st.metric("PE Ratio", f"{info.get('trailingPE', 'N/A')}")

        # Main Chart
        st.markdown("### Market Trajectory")
        fig = go.Figure()
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ))
        
        # Moving Averages
        if show_ma20:
            df['MA20'] = df['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#38bdf8', width=1.5), name='SMA 20'))
            
        if show_ma50:
            df['MA50'] = df['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='#f43f5e', width=1.5), name='SMA 50'))

        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False,
            height=600,
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Analysis Tabs
        tab_info, tab_stats, tab_data = st.tabs(["� Intelligence", "📊 Vitality Stats", "� Historical Archive"])
        
        with tab_info:
            st.markdown(f"#### Business Outlook")
            st.write(info.get('longBusinessSummary', "Operational profile not available at this time."))
            
            inf1, inf2, inf3 = st.columns(3)
            with inf1:
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {info.get('industry', 'N/A')}")
            with inf2:
                st.write(f"**Employees:** {info.get('fullTimeEmployees', 'N/A'):,}")
                st.write(f"**Headquarters:** {info.get('city', 'N/A')}, {info.get('country', 'N/A')}")
            with inf3:
                st.write(f"**Website:** [Access Portal]({info.get('website', '#')})")
                st.write(f"**Symbol:** {ticker_symbol}")

        with tab_stats:
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.markdown("##### Valuation Metrics")
                stats_df = pd.DataFrame({
                    "Metric": ["Trailing P/E", "Forward P/E", "Price/Sales", "Price/Book", "EV/Revenue", "EV/EBITDA"],
                    "Value": [
                        info.get('trailingPE', 'N/A'),
                        info.get('forwardPE', 'N/A'),
                        info.get('priceToSalesTrailing12Months', 'N/A'),
                        info.get('priceToBook', 'N/A'),
                        info.get('enterpriseToRevenue', 'N/A'),
                        info.get('enterpriseToEbitda', 'N/A')
                    ]
                })
                st.table(stats_df)
            
            with s_col2:
                st.markdown("##### Performance Metrics")
                perf_df = pd.DataFrame({
                    "Metric": ["Dividend Yield", "Beta (5Y)", "52 Week High", "52 Week Low", "Profit Margin", "ROE"],
                    "Value": [
                        f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A",
                        info.get('beta', 'N/A'),
                        info.get('fiftyTwoWeekHigh', 'N/A'),
                        info.get('fiftyTwoWeekLow', 'N/A'),
                        f"{info.get('profitMargins', 0)*100:.2f}%" if info.get('profitMargins') else "N/A",
                        f"{info.get('returnOnEquity', 0)*100:.2f}%" if info.get('returnOnEquity') else "N/A"
                    ]
                })
                st.table(perf_df)

        with tab_data:
            st.markdown("##### Historical Price Action")
            st.dataframe(df.sort_index(ascending=False).style.format("${:.2f}", subset=['Open', 'High', 'Low', 'Close']), use_container_width=True)

    else:
        st.error(f"⚠️ **Ticker Not Found:** {ticker_symbol}. Signal lost. Please verify the symbol.")
else:
    st.info("💡 **Awaiting Input:** Enter a ticker symbol in the tactical sidebar to begin analysis.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>"
    "Data provided by Yahoo! Finance. Analysis by SkyStock Pro Intelligence Engine.<br>"
    "© 2026 Premium Financial Solutions"
    "</div>", 
    unsafe_allow_html=True
)
