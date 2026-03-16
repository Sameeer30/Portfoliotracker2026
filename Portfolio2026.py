# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Rajasthan Food Trends 2025–2026", layout="wide")

# ─── Load & prepare data ───────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Ajmer Trend MOM  - Sheet2.csv", low_memory=False)
    df['date'] = pd.to_datetime(df['Aggregation'], format='%d/%m/%Y', errors='coerce')
    df['month'] = df['date'].dt.strftime('%b %Y')
    df['Total_ov'] = pd.to_numeric(df['Total_ov'], errors='coerce').fillna(0)
    return df

df = load_data()

# ─── Sidebar filters ───────────────────────────────────────────
st.sidebar.header("Filters")
cities = st.sidebar.multiselect("Cities", options=sorted(df['city_name'].unique()), default=["Jodhpur", "Kota"])
cuisines = st.sidebar.multiselect("Cuisines", options=sorted(df['res_cuisine_new'].dropna().unique()))
top_n = st.sidebar.slider("Top N restaurants", 5, 50, 15)

filtered = df[df['city_name'].isin(cities)]
if cuisines:
    filtered = filtered[filtered['res_cuisine_new'].isin(cuisines)]

# ─── Layout ────────────────────────────────────────────────────
st.title("Rajasthan Restaurant Momentum Tracker")
st.caption("Nov 2025 – Feb 2026 | Orders/Views proxy (Total_ov)")

col1, col2 = st.columns([3, 2])

with col1:
    # 1. Monthly trend by city
    monthly = filtered.groupby(['month', 'city_name'])['Total_ov'].sum().reset_index()
    fig1 = px.line(monthly, x='month', y='Total_ov', color='city_name',
                   title="Total Momentum by City", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Top cuisines
    cuisine_sum = filtered.groupby('res_cuisine_new')['Total_ov'].sum().nlargest(12).reset_index()
    fig2 = px.bar(cuisine_sum, x='Total_ov', y='res_cuisine_new',
                  title="Top Cuisines by Momentum", color='Total_ov')
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    # 3. Top restaurants table
    top_rest = filtered.groupby(['res_name', 'city_name', 'res_cuisine_new'])['Total_ov'].sum().nlargest(top_n).reset_index()
    st.subheader(f"Top {top_n} Restaurants")
    st.dataframe(top_rest.style.format({"Total_ov": "{:,.0f}"}), height=500)

# Bonus: raw explorer
with st.expander("Raw Data Explorer"):
    st.dataframe(filtered)
