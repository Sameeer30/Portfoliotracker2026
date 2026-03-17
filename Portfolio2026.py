import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="2025 vs 2026 Portfolio Comparison", layout="wide")

st.title("2025 vs 2026 Restaurant Portfolio Comparison")
st.markdown("Upload your two quarterly CSV dumps and compare cuisine-wise performance, top performers, winners & losers.")

# ─── File Uploaders ────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    file_2025 = st.file_uploader("Upload 2025 Quarter CSV", type=["csv"])
with col2:
    file_2026 = st.file_uploader("Upload 2026 Quarter CSV", type=["csv"])

if not file_2025 or not file_2026:
    st.info("Please upload both CSV files to start the analysis.")
    st.stop()

# ─── Parse function (handles your repeated header format) ──
@st.cache_data
def parse_portfolio_csv(file):
    if file is None:
        return pd.DataFrame()
    
    content = file.getvalue().decode("utf-8")
    lines = content.splitlines()
    
    data = []
    current_rest = ""
    current_id = ""
    current_cuisine = ""
    
    for line in lines:
        row = [x.strip() for x in line.split(",")]
        if len(row) < 4:
            continue
            
        # New restaurant block
        if row[0] and row[0] != "" and not row[0].startswith(",,,"):
            current_rest = row[0]
            current_id = row[1]
            current_cuisine = row[2]
            
        # Metric row
        metric = row[3]
        if metric and metric.strip():
            try:
                trend = row[4] if len(row) > 4 else ""
                mom = row[5] if len(row) > 5 else ""
                jan = float(row[6]) if len(row) > 6 and row[6] else 0
                feb = float(row[7]) if len(row) > 7 and row[7] else 0
                mar = float(row[8]) if len(row) > 8 and row[8] else 0
            except:
                jan = feb = mar = 0
                
            data.append([
                current_rest, current_id, current_cuisine,
                metric, trend, mom, jan, feb, mar
            ])
    
    df = pd.DataFrame(data, columns=[
        "Restaurant", "Res_ID", "Cuisine", "Metric",
        "Trend", "MOM_%", "JAN", "FEB", "MAR"
    ])
    
    # Clean percentage & error values
    df["MOM_%"] = pd.to_numeric(df["MOM_%"].replace(["#DIV/0!","#N/A",""], pd.NA), errors='coerce')
    return df

# ─── Load & process both files ─────────────────────────────
df_2025 = parse_portfolio_csv(file_2025)
df_2026 = parse_portfolio_csv(file_2026)

if df_2025.empty or df_2026.empty:
    st.error("Could not parse one or both files. Please check CSV format.")
    st.stop()

# ─── Add year column & concat for easier comparison ────────
df_2025["Year"] = 2025
df_2026["Year"] = 2026
df = pd.concat([df_2025, df_2026], ignore_index=True)

# ─── Pivot to wide format (per restaurant + metric) ────────
pivot = df.pivot_table(
    index=["Restaurant", "Res_ID", "Cuisine", "Metric"],
    columns="Year",
    values=["JAN","FEB","MAR"],
    aggfunc="sum"
).reset_index()

# Flatten column names
pivot.columns = ['_'.join([str(c) for c in col]).strip('_') for col in pivot.columns.values]

# Calculate totals per period
for period in ["JAN","FEB","MAR"]:
    pivot[f"Total_{period}"] = pivot[[f"{period}_2025", f"{period}_2026"]].sum(axis=1, skipna=True)

# Simple YoY GMV change (only for GMV rows)
gmv = pivot[pivot["Metric"] == "GMV"].copy()
gmv["GMV_2025"] = gmv[["JAN_2025","FEB_2025","MAR_2025"]].sum(axis=1)
gmv["GMV_2026"] = gmv[["JAN_2026","FEB_2026","MAR_2026"]].sum(axis=1)
gmv["YoY_Change_%"] = ((gmv["GMV_2026"] - gmv["GMV_2025"]) / gmv["GMV_2025"].replace(0, pd.NA)) * 100
gmv["YoY_Change_%"] = gmv["YoY_Change_%"].fillna(0)

# ─── Cuisine level aggregation ─────────────────────────────
cuisine_summary = gmv.groupby("Cuisine").agg({
    "GMV_2025": "sum",
    "GMV_2026": "sum"
}).reset_index()

cuisine_summary["YoY_Change_%"] = ((cuisine_summary["GMV_2026"] - cuisine_summary["GMV_2025"]) / cuisine_summary["GMV_2025"].replace(0, pd.NA)) * 100
cuisine_summary["YoY_Change_%"] = cuisine_summary["YoY_Change_%"].fillna(0)

# ─────────────────────────────────────────────────────────────
#               D A S H B O A R D    L A Y O U T
# ─────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs(["Cuisine Comparison", "Top Restaurants", "Winners & Losers", "Raw Data"])

with tab1:
    st.subheader("Cuisine-wise GMV – 2025 vs 2026")
    
    fig_pie = px.pie(cuisine_summary, values="GMV_2026", names="Cuisine",
                     title="2026 GMV Distribution by Cuisine",
                     hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    fig_bar = px.bar(cuisine_summary, x="Cuisine", y=["GMV_2025","GMV_2026"],
                     barmode="group", title="GMV Comparison by Cuisine")
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.dataframe(cuisine_summary.style.format({
        "GMV_2025": "₹{:,.0f}",
        "GMV_2026": "₹{:,.0f}",
        "YoY_Change_%": "{:,.1f}%"
    }), use_container_width=True)

with tab2:
    st.subheader("Top 15 Restaurants by 2026 GMV")
    top = gmv.sort_values("GMV_2026", ascending=False).head(15)
    st.dataframe(top[["Restaurant","Cuisine","GMV_2025","GMV_2026","YoY_Change_%"]].style.format({
        "GMV_2025": "₹{:,.0f}",
        "GMV_2026": "₹{:,.0f}",
        "YoY_Change_%": "{:,.1f}%"
    }), hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Biggest Winners & Losers (YoY GMV change)")
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("**Top 8 Winners**")
        winners = gmv.sort_values("YoY_Change_%", ascending=False).head(8)
        st.dataframe(winners[["Restaurant","Cuisine","GMV_2025","GMV_2026","YoY_Change_%"]].style.format({
            "GMV_2025":"₹{:,.0f}", "GMV_2026":"₹{:,.0f}", "YoY_Change_%":"{:,.1f}%"
        }), hide_index=True)
    
    with colB:
        st.markdown("**Top 8 Losers**")
        losers = gmv.sort_values("YoY_Change_%").head(8)
        st.dataframe(losers[["Restaurant","Cuisine","GMV_2025","GMV_2026","YoY_Change_%"]].style.format({
            "GMV_2025":"₹{:,.0f}", "GMV_2026":"₹{:,.0f}", "YoY_Change_%":"{:,.1f}%"
        }), hide_index=True)

with tab4:
    st.subheader("Processed & Combined Data")
    st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("App built for comparing restaurant portfolio dumps | Refresh page to restart")
