"""
Life OS - Personal Command Center
A minimalist Streamlit application for tracking wealth, health, and expenses.
"""

import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client, Client
import google.generativeai as genai
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import io
from PIL import Image
import re

# ============================================================================
# PART 1: CONFIGURATION & INITIALIZATION
# ============================================================================

st.set_page_config(
    page_title="Life OS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalist dark mode with claymorphism elements
st.markdown("""
<style>
    /* Import font */
    @import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap)');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dark theme enhancements */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Claymorphism card style */
    .clay-card {
        background: linear-gradient(145deg, #1e1e2e, #2a2a3e);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 
            8px 8px 16px #151520,
            -8px -8px 16px #353548,
            inset 1px 1px 2px rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Metric styling */
    .metric-container {
        background: linear-gradient(145deg, #252535, #1a1a28);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 
            6px 6px 12px #151520,
            -6px -6px 12px #353548;
        border: 1px solid rgba(255,255,255,0.03);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d4aa, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    .metric-delta-positive {
        color: #00d4aa;
        font-size: 0.9rem;
    }
    
    .metric-delta-negative {
        color: #ff6b6b;
        font-size: 0.9rem;
    }
    
    /* Progress bar styling */
    .progress-container {
        background: #1a1a28;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 12px;
        border-radius: 6px;
        background: linear-gradient(90deg, #00d4aa, #7c3aed);
        transition: width 0.5s ease;
    }
    
    .progress-bg {
        height: 12px;
        border-radius: 6px;
        background: #2a2a3e;
        overflow: hidden;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(145deg, #7c3aed, #5b21b6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 
            4px 4px 8px #151520,
            -4px -4px 8px #353548;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 
            6px 6px 12px #151520,
            -6px -6px 12px #353548;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a28, #151520);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #7c3aed;
        display: inline-block;
    }
    
    /* Icon styling */
    .icon-3d {
        font-size: 3rem;
        filter: drop-shadow(4px 4px 8px rgba(0,0,0,0.3));
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #252535, #1a1a28);
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #7c3aed, #5b21b6);
    }
    
    /* File uploader */
    .stFileUploader {
        background: linear-gradient(145deg, #252535, #1a1a28);
        border-radius: 16px;
        padding: 1rem;
        border: 2px dashed #7c3aed;
    }
    
    /* Data editor / tables */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)
# --- 顶部导航 (手机端更友好) ---
# 不要用 st.sidebar，改用 st.segmented_control 或 st.selectbox
menu = st.selectbox(
    "Choose Service", 
    ["🏠 Dashboard", "💰 Finance", "💪 Health", "📈 Investments"],
    index=0
)

# --- 根据选择显示内容 ---
if menu == "🏠 Dashboard":
    st.title("🎯 Life OS Dashboard")
    # 这里放你原本的 Metrics 和 Charts 代码...

elif menu == "💰 Finance":
    st.title("Expense Tracking")
    # 在这里加入 st.file_uploader("Upload Receipt") 逻辑

elif menu == "💪 Health":
    st.title("Health Tracker")
    # 在这里加入 st.file_uploader("Upload Evolt") 逻辑

def init_supabase() -> Optional[Client]:
    """Initialize Supabase client from secrets."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        return None


def init_gemini():
    """Initialize Google Gemini API."""
    try:
        api_key = st.secrets["gemini"]["api_key"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        return None


# ============================================================================
# PART 2: AI LOGIC - IMAGE PROCESSING
# ============================================================================

def process_image(image_file, image_type: str, model) -> Dict[str, Any]:
    """
    Process uploaded image using Gemini Vision API.
    
    Args:
        image_file: Uploaded image file
        image_type: Either 'receipt' or 'evolt'
        model: Initialized Gemini model
    
    Returns:
        Dictionary with extracted data
    """
    if model is None:
        return {"error": "Gemini model not initialized"}
    
    try:
        # Read and encode image
        image_data = image_file.read()
        image_file.seek(0)  # Reset file pointer
        
        # Create PIL Image for Gemini
        pil_image = Image.open(io.BytesIO(image_data))
        
        if image_type == 'receipt':
            prompt = """Analyze this receipt image and extract the following information.
            Return ONLY a valid JSON object with these exact fields:
            {
                "amount": <total amount as a number, e.g., 45.50>,
                "category": "<one of: Food, Transport, Shopping, Entertainment, Utilities, Healthcare, Other>",
                "merchant": "<store/merchant name if visible>",
                "date": "<date in YYYY-MM-DD format if visible, otherwise null>",
                "items": ["<list of main items if visible>"],
                "confidence": <confidence score 0-1>
            }
            
            If you cannot read the receipt clearly, still return the JSON with your best estimates
            and a low confidence score. Do not include any markdown formatting or code blocks."""
            
        elif image_type == 'evolt':
            prompt = """Analyze this Evolt 360 body composition report image and extract the following metrics.
            Return ONLY a valid JSON object with these exact fields:
            {
                "body_fat_pct": <body fat percentage as a number, e.g., 18.5>,
                "muscle_mass": <skeletal muscle mass in kg as a number, e.g., 35.2>,
                "visceral_fat": <visceral fat level as a number>,
                "total_body_water": <total body water percentage if visible, otherwise null>,
                "basal_metabolic_rate": <BMR if visible, otherwise null>,
                "weight": <weight in kg if visible, otherwise null>,
                "confidence": <confidence score 0-1>
            }
            
            If some values are not visible, set them to null.
            Do not include any markdown formatting or code blocks."""
        else:
            return {"error": f"Unknown image type: {image_type}"}
        
        # Generate response using Gemini
        response = model.generate_content([prompt, pil_image])
        response_text = response.text.strip()
        
        # Clean up response - remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first and last lines (code block markers)
            lines = [l for l in lines if not l.startswith("```")]
            response_text = "\n".join(lines)
        
        # Parse JSON response
        result = json.loads(response_text)
        return result
        
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response: {e}", "raw_response": response_text}
    except Exception as e:
        return {"error": f"Image processing failed: {e}"}


def upload_image_to_supabase(supabase: Client, image_file, bucket: str = "receipts") -> Optional[str]:
    """Upload image to Supabase Storage and return public URL."""
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{image_file.name}"
        
        # Read file content
        file_content = image_file.read()
        image_file.seek(0)
        
        # Upload to Supabase storage
        result = supabase.storage.from_(bucket).upload(
            filename,
            file_content,
            {"content-type": image_file.type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket).get_public_url(filename)
        return public_url
        
    except Exception as e:
        st.warning(f"Image upload failed: {e}")
        return None


# ============================================================================
# PART 3: DATABASE OPERATIONS
# ============================================================================

class DatabaseManager:
    """Handles all Supabase database operations."""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    # --- Ledger (Expenses) Operations ---
    
    def add_expense(self, amount: float, category: str, note: str = "", image_url: str = None) -> bool:
        """Add a new expense entry."""
        try:
            data = {
                "amount": amount,
                "category": category,
                "note": note,
                "image_url": image_url
            }
            self.supabase.table("ledger").insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Failed to add expense: {e}")
            return False
    
    def get_expenses(self, limit: int = 100) -> pd.DataFrame:
        """Fetch recent expenses."""
        try:
            response = self.supabase.table("ledger")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Failed to fetch expenses: {e}")
            return pd.DataFrame()
    
    def get_monthly_expenses(self) -> pd.DataFrame:
        """Get expenses grouped by month and category."""
        df = self.get_expenses(limit=1000)
        if df.empty:
            return df
        
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['month'] = df['created_at'].dt.to_period('M').astype(str)
        
        return df.groupby(['month', 'category'])['amount'].sum().reset_index()
    
    # --- Physical Stats Operations ---
    
    def add_physical_stats(self, body_fat_pct: float, muscle_mass: float, visceral_fat: float) -> bool:
        """Add a new physical stats entry."""
        try:
            data = {
                "body_fat_pct": body_fat_pct,
                "muscle_mass": muscle_mass,
                "visceral_fat": visceral_fat
            }
            self.supabase.table("physical_stats").insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Failed to add physical stats: {e}")
            return False
    
    def get_physical_stats(self, limit: int = 100) -> pd.DataFrame:
        """Fetch physical stats history."""
        try:
            response = self.supabase.table("physical_stats")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Failed to fetch physical stats: {e}")
            return pd.DataFrame()
    
    def get_latest_stats(self) -> Optional[Dict]:
        """Get the most recent physical stats."""
        df = self.get_physical_stats(limit=1)
        if not df.empty:
            return df.iloc[0].to_dict()
        return None
    
    # --- Investments Operations ---
    
    def add_investment(self, symbol: str, purchase_price: float, quantity: float, total_invested: float) -> bool:
        """Add a new investment entry."""
        try:
            data = {
                "symbol": symbol,
                "purchase_price": purchase_price,
                "quantity": quantity,
                "total_invested": total_invested
            }
            self.supabase.table("investments").insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Failed to add investment: {e}")
            return False
    
    def get_investments(self) -> pd.DataFrame:
        """Fetch all investments."""
        try:
            response = self.supabase.table("investments")\
                .select("*")\
                .order("created_at", desc=True)\
                .execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Failed to fetch investments: {e}")
            return pd.DataFrame()
    
    def get_total_invested(self, symbol: str = "NDX") -> float:
        """Get total amount invested in a symbol."""
        df = self.get_investments()
        if df.empty:
            return 0.0
        
        symbol_df = df[df['symbol'] == symbol]
        return symbol_df['total_invested'].sum() if not symbol_df.empty else 0.0
    
    def get_total_units(self, symbol: str = "NDX") -> float:
        """Get total units owned of a symbol."""
        df = self.get_investments()
        if df.empty:
            return 0.0
        
        symbol_df = df[df['symbol'] == symbol]
        return symbol_df['quantity'].sum() if not symbol_df.empty else 0.0


# ============================================================================
# PART 4: MARKET DATA
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_ndx_data() -> Tuple[float, float, pd.DataFrame]:
    """
    Fetch Nasdaq-100 (NDX) data using yfinance.
    Returns: (current_price, daily_change_pct, historical_df)
    """
    try:
        # Use QQQ as proxy for NDX (more liquid and accessible)
        ticker = yf.Ticker("QQQ")
        
        # Get current info
        info = ticker.info
        current_price = info.get('regularMarketPrice', info.get('previousClose', 0))
        prev_close = info.get('previousClose', current_price)
        
        daily_change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
        
        # Get historical data (1 year)
        hist = ticker.history(period="1y")
        hist = hist.reset_index()
        hist['Date'] = pd.to_datetime(hist['Date']).dt.date
        
        return current_price, daily_change_pct, hist
        
    except Exception as e:
        st.warning(f"Failed to fetch market data: {e}")
        return 0.0, 0.0, pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_usd_myr_rate() -> float:
    """Fetch USD to MYR exchange rate."""
    try:
        ticker = yf.Ticker("MYR=X")
        info = ticker.info
        return info.get('regularMarketPrice', info.get('previousClose', 4.50))
    except Exception:
        return 4.50  # Fallback rate


# ============================================================================
# PART 5: UI COMPONENTS
# ============================================================================

def render_metric_card(label: str, value: str, delta: str = None, delta_positive: bool = True, icon: str = "📊"):
    """Render a claymorphism-styled metric card."""
    delta_html = ""
    if delta:
        delta_class = "metric-delta-positive" if delta_positive else "metric-delta-negative"
        delta_symbol = "↑" if delta_positive else "↓"
        delta_html = f'<div class="{delta_class}">{delta_symbol} {delta}</div>'
    
    st.markdown(f"""
    <div class="metric-container">
        <div class="icon-3d">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(label: str, current: float, target: float, unit: str = ""):
    """Render a styled progress bar."""
    percentage = min((current / target * 100) if target else 0, 100)
    
    st.markdown(f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #ccc;">{label}</span>
            <span style="color: #888;">{current:.1f}{unit} / {target:.0f}{unit}</span>
        </div>
        <div class="progress-bg">
            <div class="progress-bar" style="width: {percentage}%;"></div>
        </div>
        <div style="text-align: right; margin-top: 4px; color: #7c3aed; font-weight: 600;">
            {percentage:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, icon: str = ""):
    """Render a styled section header."""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
        <span class="icon-3d">{icon}</span>
        <span class="section-header">{title}</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# PART 6: PAGE RENDERERS
# ============================================================================

def render_dashboard(db: DatabaseManager):
    """Render the main dashboard page."""
    st.title("🎯 Life OS Dashboard")
    st.caption("Your personal command center for wealth, health, and life optimization")
    
    st.markdown("---")
    
    # Get latest data
    latest_stats = db.get_latest_stats()
    total_invested = db.get_total_invested("NDX")
    total_units = db.get_total_units("NDX")
    ndx_price, ndx_change, _ = get_ndx_data()
    usd_myr = get_usd_myr_rate()
    
    # Calculate portfolio value
    portfolio_value_usd = total_units * ndx_price
    portfolio_value_myr = portfolio_value_usd * usd_myr
    portfolio_gain = portfolio_value_myr - total_invested
    portfolio_gain_pct = (portfolio_gain / total_invested * 100) if total_invested else 0
    
    # Get monthly expenses
    expenses_df = db.get_expenses(limit=1000)
    current_month_expenses = 0.0
    if not expenses_df.empty:
        expenses_df['created_at'] = pd.to_datetime(expenses_df['created_at'])
        current_month = datetime.now().strftime('%Y-%m')
        current_month_df = expenses_df[expenses_df['created_at'].dt.strftime('%Y-%m') == current_month]
        current_month_expenses = current_month_df['amount'].sum() if not current_month_df.empty else 0.0
    
    # KPI Row
    render_section_header("Key Metrics", "📈")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Portfolio Value",
            f"RM {portfolio_value_myr:,.0f}",
            f"{portfolio_gain_pct:.1f}%",
            portfolio_gain_pct >= 0,
            "💰"
        )
    
    with col2:
        render_metric_card(
            "Total Invested",
            f"RM {total_invested:,.0f}",
            f"{total_invested/12000*100:.0f}% of yearly goal",
            True,
            "📊"
        )
    
    with col3:
        body_fat = latest_stats.get('body_fat_pct', 0) if latest_stats else 0
        render_metric_card(
            "Body Fat %",
            f"{body_fat:.1f}%",
            "Target: 15%",
            body_fat <= 18,
            "💪"
        )
    
    with col4:
        render_metric_card(
            "Monthly Expenses",
            f"RM {current_month_expenses:,.0f}",
            f"Budget: RM 3,000",
            current_month_expenses <= 3000,
            "🧾"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Life Progress Bars
    render_section_header("Life Progress", "🎯")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        st.subheader("💰 Wealth Building")
        
        # Yearly DCA goal: RM 12,000 (RM 1,000 × 12 months)
        yearly_goal = 12000
        render_progress_bar("Yearly DCA Goal", total_invested, yearly_goal, " RM")
        
        # Net worth target (example: RM 100,000)
        net_worth_target = 100000
        render_progress_bar("Net Worth Target", portfolio_value_myr, net_worth_target, " RM")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        st.subheader("💪 Body Composition")
        
        if latest_stats:
            # Body fat goal: 15%
            current_bf = latest_stats.get('body_fat_pct', 20)
            # Invert for progress (lower is better)
            bf_progress = max(0, 30 - current_bf)  # Start from 30%
            bf_target = 30 - 15  # Target 15%
            render_progress_bar("Body Fat Goal (→15%)", bf_progress, bf_target, "%")
            
            # Muscle mass goal (example: 40kg)
            muscle = latest_stats.get('muscle_mass', 30)
            render_progress_bar("Muscle Mass Goal", muscle, 40, " kg")
        else:
            st.info("No body composition data yet. Add your first Evolt scan!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        st.subheader("📈 Portfolio Growth")
        
        investments_df = db.get_investments()
        if not investments_df.empty:
            investments_df['created_at'] = pd.to_datetime(investments_df['created_at'])
            investments_df = investments_df.sort_values('created_at')
            investments_df['cumulative_invested'] = investments_df['total_invested'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=investments_df['created_at'],
                y=investments_df['cumulative_invested'],
                mode='lines+markers',
                name='Total Invested',
                line=dict(color='#7c3aed', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(124, 58, 237, 0.2)'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No investment data yet. Start your DCA journey!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        st.subheader("📊 Expense Breakdown")
        
        if not expenses_df.empty:
            category_totals = expenses_df.groupby('category')['amount'].sum().reset_index()
            
            fig = px.pie(
                category_totals,
                values='amount',
                names='category',
                hole=0.6,
                color_discrete_sequence=['#7c3aed', '#00d4aa', '#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#ff8c42']
            )
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data yet. Start tracking!")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_finance_page(db: DatabaseManager, gemini_model, supabase: Client):
    """Render the finance page with receipt scanner and portfolio tracker."""
    st.title("💰 Finance Hub")
    st.caption("Track investments and expenses with AI-powered receipt scanning")
    
    tab1, tab2, tab3 = st.tabs(["📊 Portfolio", "🧾 Receipt Scanner", "📝 Manual Entry"])
    
    with tab1:
        render_section_header("Nasdaq-100 DCA Tracker", "📈")
        
        # Fetch market data
        ndx_price, ndx_change, hist_df = get_ndx_data()
        usd_myr = get_usd_myr_rate()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            render_metric_card(
                "QQQ Price (USD)",
                f"${ndx_price:.2f}",
                f"{ndx_change:+.2f}%",
                ndx_change >= 0,
                "📊"
            )
        
        with col2:
            render_metric_card(
                "USD/MYR Rate",
                f"{usd_myr:.4f}",
                icon="💱"
            )
        
        with col3:
            total_units = db.get_total_units("NDX")
            total_invested = db.get_total_invested("NDX")
            current_value = total_units * ndx_price * usd_myr
            gain_loss = current_value - total_invested
            render_metric_card(
                "Unrealized P&L",
                f"RM {gain_loss:+,.0f}",
                f"{(gain_loss/total_invested*100):+.1f}%" if total_invested else "0%",
                gain_loss >= 0,
                "📈" if gain_loss >= 0 else "📉"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Price chart
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        st.subheader("1-Year Price History")
        
        if not hist_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist_df['Date'],
                y=hist_df['Close'],
                mode='lines',
                name='QQQ',
                line=dict(color='#00d4aa', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 212, 170, 0.1)'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                height=350,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Price (USD)'),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add DCA Entry
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        st.subheader("➕ Record DCA Purchase")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dca_amount_myr = st.number_input("Amount (RM)", value=1000.0, min_value=0.0, step=100.0)
        with col2:
            purchase_price_usd = st.number_input("Purchase Price (USD)", value=ndx_price, min_value=0.0, step=1.0)
        with col3:
            # Calculate units
            amount_usd = dca_amount_myr / usd_myr
            units = amount_usd / purchase_price_usd if purchase_price_usd else 0
            st.metric("Units to Purchase", f"{units:.4f}")
        
        if st.button("💾 Record Investment", key="record_investment"):
            if db.add_investment("NDX", purchase_price_usd, units, dca_amount_myr):
                st.success(f"Recorded: {units:.4f} units @ ${purchase_price_usd:.2f}")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Investment History
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📜 Investment History")
        
        investments_df = db.get_investments()
        if not investments_df.empty:
            display_df = investments_df[['created_at', 'symbol', 'purchase_price', 'quantity', 'total_invested']].copy()
            display_df.columns = ['Date', 'Symbol', 'Price (USD)', 'Units', 'Invested (RM)']
            display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No investments recorded yet.")
    
    with tab2:
        render_section_header("AI Receipt Scanner", "📸")
        
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload receipt image",
                type=['png', 'jpg', 'jpeg'],
                key="receipt_upload"
            )
            
            camera_input = st.camera_input("Or take a photo", key="receipt_camera")
        
        image_to_process = uploaded_file or camera_input
        
        with col2:
            if image_to_process:
                st.image(image_to_process, caption="Receipt Preview", use_container_width=True)
        
        if image_to_process and st.button("🔍 Analyze Receipt", key="analyze_receipt"):
            with st.spinner("Processing receipt with AI..."):
                result = process_image(image_to_process, 'receipt', gemini_model)
                
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success("Receipt analyzed successfully!")
                    
                    st.session_state['receipt_data'] = result
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Amount", f"RM {result.get('amount', 0):.2f}")
                    with col2:
                        st.metric("Category", result.get('category', 'Unknown'))
                    with col3:
                        confidence = result.get('confidence', 0) * 100
                        st.metric("Confidence", f"{confidence:.0f}%")
                    
                    if result.get('merchant'):
                        st.info(f"🏪 Merchant: {result['merchant']}")
                    
                    if result.get('items'):
                        with st.expander("📋 Items detected"):
                            for item in result['items']:
                                st.write(f"• {item}")
        
        # Save extracted data
        if 'receipt_data' in st.session_state:
            st.markdown("---")
            st.subheader("Confirm & Save")
            
            data = st.session_state['receipt_data']
            
            col1, col2 = st.columns(2)
            with col1:
                final_amount = st.number_input(
                    "Amount (RM)", 
                    value=float(data.get('amount', 0)),
                    min_value=0.0,
                    key="final_amount"
                )
            with col2:
                final_category = st.selectbox(
                    "Category",
                    ['Food', 'Transport', 'Shopping', 'Entertainment', 'Utilities', 'Healthcare', 'Other'],
                    index=['Food', 'Transport', 'Shopping', 'Entertainment', 'Utilities', 'Healthcare', 'Other'].index(data.get('category', 'Other')),
                    key="final_category"
                )
            
            final_note = st.text_input("Note", value=data.get('merchant', ''), key="final_note")
            
            if st.button("💾 Save Expense", key="save_receipt_expense"):
                # Upload image
                image_url = None
                if supabase and image_to_process:
                    image_to_process.seek(0)
                    image_url = upload_image_to_supabase(supabase, image_to_process)
                
                if db.add_expense(final_amount, final_category, final_note, image_url):
                    st.success("Expense saved!")
                    del st.session_state['receipt_data']
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        render_section_header("Manual Expense Entry", "✏️")
        
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            manual_amount = st.number_input("Amount (RM)", min_value=0.0, step=1.0, key="manual_amount")
            manual_category = st.selectbox(
                "Category",
                ['Food', 'Transport', 'Shopping', 'Entertainment', 'Utilities', 'Healthcare', 'Other'],
                key="manual_category"
            )
        
        with col2:
            manual_note = st.text_area("Note", key="manual_note", height=100)
        
        if st.button("💾 Add Expense", key="add_manual_expense"):
            if manual_amount > 0:
                if db.add_expense(manual_amount, manual_category, manual_note):
                    st.success(f"Added: RM {manual_amount:.2f} - {manual_category}")
                    st.rerun()
            else:
                st.warning("Please enter an amount greater than 0")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent expenses
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📜 Recent Expenses")
        
        expenses_df = db.get_expenses(limit=20)
        if not expenses_df.empty:
            display_df = expenses_df[['created_at', 'amount', 'category', 'note']].copy()
            display_df.columns = ['Date', 'Amount (RM)', 'Category', 'Note']
            display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No expenses recorded yet.")


def render_health_page(db: DatabaseManager, gemini_model):
    """Render the health tracking page."""
    st.title("💪 Health Hub")
    st.caption("Track body composition with Evolt 360 integration")
    
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📸 Evolt Scanner", "✏️ Manual Entry"])
    
    with tab1:
        render_section_header("Body Composition", "🏋️")
        
        # Get latest and historical stats
        latest_stats = db.get_latest_stats()
        stats_df = db.get_physical_stats()
        
        if latest_stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                bf = latest_stats.get('body_fat_pct', 0)
                # Calculate delta from previous
                delta = None
                if len(stats_df) > 1:
                    prev_bf = stats_df.iloc[1].get('body_fat_pct', bf)
                    delta = f"{bf - prev_bf:+.1f}%"
                render_metric_card(
                    "Body Fat %",
                    f"{bf:.1f}%",
                    delta,
                    bf <= 18 if delta else True,
                    "🔥"
                )
            
            with col2:
                mm = latest_stats.get('muscle_mass', 0)
                delta = None
                if len(stats_df) > 1:
                    prev_mm = stats_df.iloc[1].get('muscle_mass', mm)
                    delta = f"{mm - prev_mm:+.1f}kg"
                render_metric_card(
                    "Muscle Mass",
                    f"{mm:.1f}kg",
                    delta,
                    mm >= 35 if delta else True,
                    "💪"
                )
            
            with col3:
                vf = latest_stats.get('visceral_fat', 0)
                delta = None
                if len(stats_df) > 1:
                    prev_vf = stats_df.iloc[1].get('visceral_fat', vf)
                    delta = f"{vf - prev_vf:+.1f}"
                render_metric_card(
                    "Visceral Fat",
                    f"{vf:.0f}",
                    delta,
                    vf <= 10 if delta else True,
                    "🫀"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Trend Charts
            if len(stats_df) >= 2:
                stats_df['created_at'] = pd.to_datetime(stats_df['created_at'])
                stats_df = stats_df.sort_values('created_at')
                
                st.markdown('<div class="clay-card">', unsafe_allow_html=True)
                st.subheader("📈 Progress Over Time")
                
                fig = make_subplots(
                    rows=1, cols=3,
                    subplot_titles=['Body Fat %', 'Muscle Mass (kg)', 'Visceral Fat'],
                    horizontal_spacing=0.1
                )
                
                # Body Fat
                fig.add_trace(
                    go.Scatter(
                        x=stats_df['created_at'],
                        y=stats_df['body_fat_pct'],
                        mode='lines+markers',
                        name='Body Fat',
                        line=dict(color='#ff6b6b', width=3),
                        marker=dict(size=8)
                    ),
                    row=1, col=1
                )
                # Add target line
                fig.add_hline(y=15, line_dash="dash", line_color="#00d4aa", row=1, col=1)
                
                # Muscle Mass
                fig.add_trace(
                    go.Scatter(
                        x=stats_df['created_at'],
                        y=stats_df['muscle_mass'],
                        mode='lines+markers',
                        name='Muscle',
                        line=dict(color='#7c3aed', width=3),
                        marker=dict(size=8)
                    ),
                    row=1, col=2
                )
                # Add target line
                fig.add_hline(y=40, line_dash="dash", line_color="#00d4aa", row=1, col=2)
                
                # Visceral Fat
                fig.add_trace(
                    go.Scatter(
                        x=stats_df['created_at'],
                        y=stats_df['visceral_fat'],
                        mode='lines+markers',
                        name='Visceral',
                        line=dict(color='#ffd93d', width=3),
                        marker=dict(size=8)
                    ),
                    row=1, col=3
                )
                # Add target line
                fig.add_hline(y=10, line_dash="dash", line_color="#00d4aa", row=1, col=3)
                
                fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=350,
                    showlegend=False,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
                
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Dashed lines show targets: 15% body fat, 40kg muscle, ≤10 visceral fat")
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Add more measurements to see progress trends!")
        else:
            st.info("No body composition data yet. Start by scanning your Evolt report or entering data manually!")
    
    with tab2:
        render_section_header("Evolt 360 Report Scanner", "📸")
        
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            evolt_file = st.file_uploader(
                "Upload Evolt 360 report image",
                type=['png', 'jpg', 'jpeg'],
                key="evolt_upload"
            )
            
            evolt_camera = st.camera_input("Or take a photo of the report", key="evolt_camera")
        
        evolt_image = evolt_file or evolt_camera
        
        with col2:
            if evolt_image:
                st.image(evolt_image, caption="Evolt Report Preview", use_container_width=True)
        
        if evolt_image and st.button("🔍 Analyze Report", key="analyze_evolt"):
            with st.spinner("Processing Evolt report with AI..."):
                result = process_image(evolt_image, 'evolt', gemini_model)
                
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success("Report analyzed successfully!")
                    st.session_state['evolt_data'] = result
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Body Fat %", f"{result.get('body_fat_pct', 'N/A')}")
                    with col2:
                        st.metric("Muscle Mass", f"{result.get('muscle_mass', 'N/A')} kg")
                    with col3:
                        st.metric("Visceral Fat", f"{result.get('visceral_fat', 'N/A')}")
                    
                    if result.get('weight'):
                        st.info(f"⚖️ Weight: {result['weight']} kg")
                    if result.get('basal_metabolic_rate'):
                        st.info(f"🔥 BMR: {result['basal_metabolic_rate']} kcal")
        
        # Save extracted data
        if 'evolt_data' in st.session_state:
            st.markdown("---")
            st.subheader("Confirm & Save")
            
            data = st.session_state['evolt_data']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                final_bf = st.number_input(
                    "Body Fat %",
                    value=float(data.get('body_fat_pct', 0) or 0),
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key="final_bf"
                )
            
            with col2:
                final_mm = st.number_input(
                    "Muscle Mass (kg)",
                    value=float(data.get('muscle_mass', 0) or 0),
                    min_value=0.0,
                    step=0.1,
                    key="final_mm"
                )
            
            with col3:
                final_vf = st.number_input(
                    "Visceral Fat",
                    value=float(data.get('visceral_fat', 0) or 0),
                    min_value=0.0,
                    step=1.0,
                    key="final_vf"
                )
            
            if st.button("💾 Save Stats", key="save_evolt"):
                if db.add_physical_stats(final_bf, final_mm, final_vf):
                    st.success("Body composition data saved!")
                    del st.session_state['evolt_data']
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        render_section_header("Manual Entry", "✏️")
        
        st.markdown('<div class="clay-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            manual_bf = st.number_input(
                "Body Fat %",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="manual_bf"
            )
        
        with col2:
            manual_mm = st.number_input(
                "Muscle Mass (kg)",
                min_value=0.0,
                step=0.1,
                key="manual_mm"
            )
        
        with col3:
            manual_vf = st.number_input(
                "Visceral Fat Level",
                min_value=0.0,
                step=1.0,
                key="manual_vf"
            )
        
        if st.button("💾 Save Entry", key="save_manual_stats"):
            if manual_bf > 0 or manual_mm > 0:
                if db.add_physical_stats(manual_bf, manual_mm, manual_vf):
                    st.success("Stats saved successfully!")
                    st.rerun()
            else:
                st.warning("Please enter at least one metric")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # History
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📜 History")
        
        stats_df = db.get_physical_stats(limit=20)
        if not stats_df.empty:
            display_df = stats_df[['created_at', 'body_fat_pct', 'muscle_mass', 'visceral_fat']].copy()
            display_df.columns = ['Date', 'Body Fat %', 'Muscle Mass (kg)', 'Visceral Fat']
            display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No records yet.")


def render_settings_page():
    """Render the settings page."""
    st.title("⚙️ Settings")
    st.caption("Configure your Life OS preferences")
    
    st.markdown('<div class="clay-card">', unsafe_allow_html=True)
    
    st.subheader("🎯 Goals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💰 Wealth Goals**")
        yearly_dca = st.number_input("Yearly DCA Target (RM)", value=12000, step=1000)
        net_worth_target = st.number_input("Net Worth Target (RM)", value=100000, step=10000)
    
    with col2:
        st.markdown("**💪 Health Goals**")
        bf_target = st.number_input("Body Fat % Target", value=15.0, step=0.5)
        mm_target = st.number_input("Muscle Mass Target (kg)", value=40.0, step=0.5)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="clay-card">', unsafe_allow_html=True)
    st.subheader("📊 Budget Categories")
    
    categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Utilities', 'Healthcare', 'Other']
    
    budget_cols = st.columns(4)
    for i, cat in enumerate(categories):
        with budget_cols[i % 4]:
            st.number_input(f"{cat} (RM)", value=500, step=50, key=f"budget_{cat}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="clay-card">', unsafe_allow_html=True)
    st.subheader("🔐 System Info")
    
    st.info("Settings are stored in Streamlit secrets. Modify `.streamlit/secrets.toml` to update credentials and API keys.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Supabase", "✅ Connected" if st.session_state.get('supabase') else "❌ Not Connected")
    with col2:
        st.metric("Gemini AI", "✅ Ready" if st.session_state.get('gemini') else "❌ Not Ready")
    with col3:
        st.metric("Market Data", "✅ Available")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# PART 7: AUTHENTICATION
# ============================================================================

def setup_authenticator():
    """Setup streamlit-authenticator with credentials from secrets."""
    try:
        credentials = {
            'usernames': {
                st.secrets["auth"]["username"]: {
                    'name': st.secrets["auth"]["name"],
                    'password': st.secrets["auth"]["password_hash"]
                }
            }
        }
        
        authenticator = stauth.Authenticate(
            credentials,
            st.secrets["auth"]["cookie_name"],
            st.secrets["auth"]["cookie_key"],
            cookie_expiry_days=st.secrets["auth"]["cookie_expiry_days"]
        )
        
        return authenticator
    except Exception as e:
        st.error(f"Authentication setup failed: {e}")
        return None


def render_login_page(authenticator):
    """Render the login page."""
    st.markdown("""
    <div style="text-align: center; padding: 4rem 0;">
        <h1 style="font-size: 4rem; margin-bottom: 0;">🎯</h1>
        <h1 style="background: linear-gradient(135deg, #7c3aed, #00d4aa); 
                   -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent;
                   font-size: 3rem;
                   margin-bottom: 0.5rem;">Life OS</h1>
        <p style="color: #888; font-size: 1.2rem;">Your Personal Command Center</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        authenticator.login()


# ============================================================================
# PART 8: MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    # Initialize authenticator
    authenticator = setup_authenticator()
    
    if authenticator is None:
        st.error("Failed to initialize authentication. Please check your secrets configuration.")
        st.stop()
    
    # Check authentication state
    if st.session_state.get("authentication_status") is None:
        render_login_page(authenticator)
        st.stop()
    
    if st.session_state.get("authentication_status") is False:
        render_login_page(authenticator)
        st.error("Username/password is incorrect")
        st.stop()
    
    # User is authenticated
    # Initialize services
    supabase = init_supabase()
    gemini_model = init_gemini()
    
    # Store in session state for access in other functions
    st.session_state['supabase'] = supabase
    st.session_state['gemini'] = gemini_model
    
    # Initialize database manager
    db = DatabaseManager(supabase) if supabase else None
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <span style="font-size: 2rem;">🎯</span>
            <h2 style="margin: 0.5rem 0; font-size: 1.5rem;">Life OS</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        st.markdown(f"👤 **{st.session_state.get('name', 'User')}**")
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🎯 Dashboard", "💰 Finance", "💪 Health", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Logout
        authenticator.logout("🚪 Logout", "sidebar")
        
        st.markdown("---")
        
        # Quick stats
        if db:
            total_invested = db.get_total_invested("NDX")
            st.metric("Total Invested", f"RM {total_invested:,.0f}")
    
    # Main Content
    if db is None:
        st.error("Database connection failed. Please check your Supabase configuration.")
        st.stop()
    
    if page == "🎯 Dashboard":
        render_dashboard(db)
    elif page == "💰 Finance":
        render_finance_page(db, gemini_model, supabase)
    elif page == "💪 Health":
        render_health_page(db, gemini_model)
    elif page == "⚙️ Settings":
        render_settings_page()


if __name__ == "__main__":
    main()
