#!/usr/bin/env python3
"""
SwiftLogic AI — Portfolio Demo
==============================
Live Business Intelligence Dashboard for a fictional Indian D2C brand.
Built with Streamlit + Pandas + Plotly. Runs on dummy data only.

How to run:
    pip install streamlit pandas plotly numpy
    streamlit run portfolio_demo.py

This is the kind of working proof you show clients before the first call.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="SwiftLogic AI — Live Demo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean professional look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1d2e;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #5a647a;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8f9fc;
        border: 1px solid #e2e6f0;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
    }
    .stMetric {
        background: #ffffff;
        border: 1px solid #e2e6f0;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1a1d2e;
    }
    .insight-box {
        background: #fff8e6;
        border-left: 4px solid #e89b1e;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.92rem;
        color: #1a1d2e;
    }
    .footer {
        text-align: center;
        color: #8b93a7;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e2e6f0;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DUMMY DATA GENERATION
# ──────────────────────────────────────────────
@st.cache_data
def generate_data():
    np.random.seed(42)
    
    # Date range: last 12 months
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Products (typical Indian D2C / FMCG)
    products = [
        ("Organic Turmeric Powder 200g", "Health", 249),
        ("Cold-Pressed Coconut Oil 500ml", "Health", 399),
        ("Herbal Face Wash 100ml", "Personal Care", 299),
        ("Ayurvedic Hair Oil 100ml", "Personal Care", 349),
        ("Millet Cookies 200g", "Food", 199),
        ("Protein Energy Bars (Pack of 6)", "Food", 449),
        ("Stainless Steel Water Bottle 750ml", "Lifestyle", 599),
        ("Cotton Yoga Mat", "Lifestyle", 899),
        ("Neem Soap Pack (3)", "Personal Care", 179),
        ("Ashwagandha Capsules 60", "Health", 499),
    ]
    
    # Generate daily sales
    rows = []
    for d in dates:
        # Higher sales on weekends and festival-ish periods
        day_factor = 1.4 if d.weekday() >= 5 else 1.0
        month_factor = 1.3 if d.month in [10, 11, 12, 1] else 1.0  # festive season
        
        n_orders = int(np.random.poisson(18 * day_factor * month_factor))
        
        for _ in range(n_orders):
            prod_name, category, price = products[np.random.randint(0, len(products))]
            qty = np.random.randint(1, 4)
            discount = np.random.choice([0, 0, 0, 0.05, 0.10], p=[0.6, 0.15, 0.1, 0.1, 0.05])
            revenue = round(price * qty * (1 - discount), 2)
            
            rows.append({
                "date": d,
                "order_id": f"ORD-{d.strftime('%Y%m%d')}-{np.random.randint(1000,9999)}",
                "product": prod_name,
                "category": category,
                "quantity": qty,
                "unit_price": price,
                "discount": discount,
                "revenue": revenue,
                "customer_id": f"CUST-{np.random.randint(1000, 1800)}",
                "city": np.random.choice(
                    ["Mumbai", "Pune", "Bengaluru", "Delhi", "Hyderabad", "Chennai", "Ahmedabad", "Jaipur"],
                    p=[0.22, 0.18, 0.15, 0.12, 0.10, 0.09, 0.08, 0.06]
                ),
                "channel": np.random.choice(["Website", "Amazon", "WhatsApp", "Instagram"], p=[0.35, 0.30, 0.20, 0.15])
            })
    
    sales_df = pd.DataFrame(rows)
    
    # Customer summary for RFM
    customer_df = sales_df.groupby("customer_id").agg(
        recency=("date", lambda x: (end_date - x.max().date()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum")
    ).reset_index()
    
    # Simple RFM scoring
    customer_df["R_score"] = pd.qcut(customer_df["recency"], 4, labels=[4,3,2,1]).astype(int)
    customer_df["F_score"] = pd.qcut(customer_df["frequency"].rank(method="first"), 4, labels=[1,2,3,4]).astype(int)
    customer_df["M_score"] = pd.qcut(customer_df["monetary"], 4, labels=[1,2,3,4]).astype(int)
    customer_df["RFM_score"] = customer_df["R_score"] + customer_df["F_score"] + customer_df["M_score"]
    
    def segment(score):
        if score >= 10: return "Champions"
        elif score >= 8: return "Loyal"
        elif score >= 6: return "Potential"
        elif score >= 4: return "At Risk"
        else: return "Lost"
    
    customer_df["segment"] = customer_df["RFM_score"].apply(segment)
    
    # Inventory snapshot
    inventory = []
    for prod_name, category, price in products:
        stock = np.random.randint(20, 280)
        threshold = np.random.randint(30, 60)
        inventory.append({
            "product": prod_name,
            "category": category,
            "current_stock": stock,
            "reorder_level": threshold,
            "unit_cost": round(price * 0.45, 2),
            "status": "Low" if stock < threshold else "Healthy"
        })
    inv_df = pd.DataFrame(inventory)
    
    return sales_df, customer_df, inv_df

sales_df, customer_df, inv_df = generate_data()

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ SwiftLogic AI")
    st.markdown("**Portfolio Demo**")
    st.caption("Built for client conversations")
    st.markdown("---")
    
    st.markdown("**Demo Business**")
    st.markdown("🌿 **Prakriti Naturals**")
    st.caption("Fictional D2C brand · Pune")
    st.caption("Health • Personal Care • Lifestyle")
    
    st.markdown("---")
    period = st.selectbox(
        "Time Period",
        ["Last 30 days", "Last 90 days", "Last 12 months"],
        index=2
    )
    
    if period == "Last 30 days":
        cutoff = datetime.now().date() - timedelta(days=30)
    elif period == "Last 90 days":
        cutoff = datetime.now().date() - timedelta(days=90)
    else:
        cutoff = sales_df["date"].min().date()
    
    filtered = sales_df[sales_df["date"].dt.date >= cutoff]
    
    st.markdown("---")
    st.markdown("**What this demo shows**")
    st.markdown("""
    - Live sales analytics  
    - Customer RFM segmentation  
    - Inventory health  
    - Channel performance  
    - Actionable insights  
    """)
    st.markdown("---")
    st.caption("All data is dummy & generated for demo purposes.")

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown('<div class="main-header">Prakriti Naturals — Live Business Dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Real-time view of sales, customers & inventory · Data as of {datetime.now().strftime("%d %b %Y")}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────
total_revenue = filtered["revenue"].sum()
total_orders = filtered["order_id"].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
unique_customers = filtered["customer_id"].nunique()
low_stock_count = (inv_df["status"] == "Low").sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Avg Order Value", f"₹{avg_order_value:,.0f}")
col4.metric("Active Customers", f"{unique_customers:,}")
col5.metric("Low Stock SKUs", f"{low_stock_count}", delta="Needs attention" if low_stock_count > 0 else "Healthy", delta_color="inverse")

st.markdown("")

# ──────────────────────────────────────────────
# MAIN CHARTS
# ──────────────────────────────────────────────
left, right = st.columns([1.6, 1])

with left:
    st.subheader("Revenue Trend")
    daily = filtered.groupby(filtered["date"].dt.date)["revenue"].sum().reset_index()
    daily.columns = ["date", "revenue"]
    
    fig = px.area(
        daily, x="date", y="revenue",
        labels={"revenue": "Revenue (₹)", "date": ""},
    )
    fig.update_traces(line_color="#e89b1e", fillcolor="rgba(232,155,30,0.15)")
    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0"),
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Revenue by Category")
    cat = filtered.groupby("category")["revenue"].sum().reset_index().sort_values("revenue", ascending=True)
    fig2 = px.bar(
        cat, x="revenue", y="category", orientation="h",
        labels={"revenue": "Revenue (₹)", "category": ""},
        color_discrete_sequence=["#0d9b7a"]
    )
    fig2.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0"),
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

# ──────────────────────────────────────────────
# SECOND ROW
# ──────────────────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Top Products")
    top_prod = (
        filtered.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(6)
        .reset_index()
    )
    top_prod["revenue"] = top_prod["revenue"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(top_prod, use_container_width=True, hide_index=True)

with c2:
    st.subheader("Channel Performance")
    channel = filtered.groupby("channel")["revenue"].sum().reset_index()
    fig3 = px.pie(
        channel, values="revenue", names="channel",
        color_discrete_sequence=["#e89b1e", "#0d9b7a", "#5a647a", "#7c5cbf"]
    )
    fig3.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=True
    )
    st.plotly_chart(fig3, use_container_width=True)

with c3:
    st.subheader("Top Cities")
    city = (
        filtered.groupby("city")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(6)
        .reset_index()
    )
    city["revenue"] = city["revenue"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(city, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────
# RFM SEGMENTATION
# ──────────────────────────────────────────────
st.markdown("---")
st.subheader("Customer Segmentation (RFM)")

seg_counts = customer_df["segment"].value_counts().reindex(
    ["Champions", "Loyal", "Potential", "At Risk", "Lost"]
).fillna(0).astype(int)

seg_col1, seg_col2 = st.columns([1.2, 1.5])

with seg_col1:
    fig4 = px.bar(
        x=seg_counts.index,
        y=seg_counts.values,
        labels={"x": "Segment", "y": "Customers"},
        color=seg_counts.index,
        color_discrete_map={
            "Champions": "#0d9b7a",
            "Loyal": "#2ecc71",
            "Potential": "#e89b1e",
            "At Risk": "#e67e22",
            "Lost": "#e55a5a"
        }
    )
    fig4.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        yaxis=dict(gridcolor="#f0f0f0")
    )
    st.plotly_chart(fig4, use_container_width=True)

with seg_col2:
    st.markdown("**What the segments mean**")
    st.markdown("""
    | Segment | Meaning | Recommended Action |
    |---------|---------|---------------------|
    | **Champions** | Buy often & recently | Reward + early access |
    | **Loyal** | Consistent buyers | Upsell & loyalty program |
    | **Potential** | Growing interest | Nurture with offers |
    | **At Risk** | Used to buy, slowing down | Win-back campaign |
    | **Lost** | Haven't bought in long time | Re-engagement or ignore |
    """)

# Insight box
champions = (customer_df["segment"] == "Champions").sum()
at_risk = (customer_df["segment"] == "At Risk").sum()
st.markdown(f"""
<div class="insight-box">
<strong>💡 Insight:</strong> You have <strong>{champions} Champions</strong> driving a large share of revenue. 
At the same time, <strong>{at_risk} customers are At Risk</strong>. 
A simple WhatsApp win-back sequence for the At Risk group usually recovers 15–25% of them within 2 weeks.
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# INVENTORY
# ──────────────────────────────────────────────
st.markdown("---")
st.subheader("Inventory Health")

inv_col1, inv_col2 = st.columns([1.5, 1])

with inv_col1:
    inv_display = inv_df.copy()
    inv_display["status_icon"] = inv_display["status"].map({"Low": "🔴 Low", "Healthy": "🟢 Healthy"})
    st.dataframe(
        inv_display[["product", "category", "current_stock", "reorder_level", "status_icon"]].rename(columns={
            "product": "Product",
            "category": "Category",
            "current_stock": "Stock",
            "reorder_level": "Reorder Level",
            "status_icon": "Status"
        }),
        use_container_width=True,
        hide_index=True
    )

with inv_col2:
    low = inv_df[inv_df["status"] == "Low"]
    if len(low) > 0:
        st.warning(f"**{len(low)} products** need reordering soon.")
        for _, row in low.iterrows():
            st.markdown(f"- **{row['product']}** — only {row['current_stock']} left (reorder at {row['reorder_level']})")
    else:
        st.success("All products are above reorder level.")

# ──────────────────────────────────────────────
# FOOTER / CTA
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="footer">
    <strong>SwiftLogic AI</strong> · Portfolio Demo<br>
    This dashboard is built with Python (Streamlit + Pandas + Plotly) using only dummy data.<br>
    Want something like this for your business? <a href="https://wa.me/919692514547" target="_blank">Book a free 30-min audit</a>
</div>
""", unsafe_allow_html=True)
