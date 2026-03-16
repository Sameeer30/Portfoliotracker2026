import streamlit as st
import pandas as pd
import plotly.express as px
import io
from collections import Counter

# ────────────────────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sameer's Portfolio Tracker",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Sameer's Portfolio Tracker – Rajasthan Restaurants")
st.markdown("**MoM Portfolio & Restaurant Dashboard** | Upload your CSVs for full data")

# ────────────────────────────────────────────────────────────────
# Demo data (your truncated samples)
# ────────────────────────────────────────────────────────────────
MONTHLY_DEMO_CSV = """
,,2025-07,2025-08,2025-09,2025-10,2025-11,2025-12,2026-01,2026-02,2026-03
Orders,Total_OV,12131,15374,14152,15200,13936,15060,16962,15493,8539
,Ads_ov,3237,4069,3709,3819,5392,7469,8511,9522,5407
,Ads_ov%,26.68%,26.47%,26.21%,25.13%,38.69%,49.59%,50.18%,61.46%,63.32%
Revenue,Subtotal Value,4190088,5472950,5031388,5671928,4897425,5415835,5837830,5314038,3005760
,PC,29635,34297,38251,33995,29669,38307,47282,41050,25868
,Subtotal+PC,4219722,5507248,5069640,5705924,4927095,5454142,5885112,5355088,3031628
,CV,3281877,4073163,3627935,4276811,3686141,4100899,4509484,4152037,2345242
,GMV,4687002,6097418,5609099,6297233,5453290,6030471,6512704,5933419,3354231
,ACV,271,265,256,281,265,272,266,268,275
,AOV,386,397,396,414,391,400,384,383,393
,MVD,677823,739525,644094,768963,657168,760835,843438,683130,411472
,MVD Discount%,16.18%,13.51%,12.80%,13.56%,13.42%,14.05%,14.45%,12.86%,13.69%
,MVDPO,56,48,46,51,47,51,50,44,48
,Salt,218854,647387,761163,611190,542317,547822,473148,480706,248833
,Salt Discount %,5.22%,11.83%,15.13%,10.78%,11.07%,10.12%,8.10%,9.05%,8.28%
,SALTPO,18,42,54,40,39,36,28,31,29
,ZVD,137919,158593,122549,137336,141211,189733,262808,225087,144906
,ZVD Discount %,3.29%,2.90%,2.44%,2.42%,2.88%,3.50%,4.50%,4.24%,4.82%
,ZVDPO,11,10,9,9,10,13,15,15,17
"""

RES_DEMO_CSV = """
Aggregation,city_name,subzone,res_name,lvl,Total_ov,res_cuisine_new
1/1/2026,Ajmer,All_subzone,Life Is Tea,19527478,21,street food
1/1/2026,Kota,All_subzone,Cakey 'N' Bakey,18857028,47,cakes
12/1/2025,Kota,All_subzone,Jain Fast Foods,19703987,,na
2/1/2026,Kota,All_subzone,Paratha Aunty,22530629,4,north indian
2/1/2026,Kota,All_subzone,subway,20696973,576,"wraps, rolls and sandwiches"
1/1/2026,Jodhpur,All_subzone,Momo's Wala,19859957,12,street food
"""

# ────────────────────────────────────────────────────────────────
# Uploaders
# ────────────────────────────────────────────────────────────────
monthly_upload = st.file_uploader("Upload Monthly Portfolio CSV", type="csv")
res_upload     = st.file_uploader("Upload Restaurant MoM CSV", type="csv")

# ────────────────────────────────────────────────────────────────
# Load monthly data
# ────────────────────────────────────────────────────────────────
monthly_source = monthly_upload if monthly_upload else io.StringIO(MONTHLY_DEMO_CSV)

df_monthly_raw = pd.read_csv(monthly_source, header=None)

# Forward fill the section names (first column)
df_monthly_raw.iloc[:, 0] = df_monthly_raw.iloc[:, 0].ffill()

# Transpose → months become rows
df_monthly = df_monthly_raw.set_index(0).T.reset_index(drop=True)

# Build clean column names
clean_cols = []
current_section = None

for val in df_monthly.columns:
    if pd.isna(val) or str(val).strip() == '':
        name = current_section if current_section else "Unnamed"
    else:
        current_section = str(val).strip()
        name = current_section

    clean_cols.append(name)

# Handle duplicate names by adding counter
counts = Counter()
final_cols = []
for name in clean_cols:
    counts[name] += 1
    if counts[name] > 1:
        final_cols.append(f"{name}_{counts[name]}")
    else:
        final_cols.append(name)

df_monthly.columns = final_cols

# Convert to numeric
df_monthly = df_monthly.apply(pd.to_numeric, errors='coerce')

# ────────────────────────────────────────────────────────────────
# Load restaurant data
# ────────────────────────────────────────────────────────────────
res_source = res_upload if res_upload else io.StringIO(RES_DEMO_CSV)

df_res = pd.read_csv(res_source)
df_res['Aggregation'] = pd.to_datetime(df_res['Aggregation'], format='%m/%d/%Y', errors='coerce')
df_res['Month'] = df_res['Aggregation'].dt.strftime('%Y-%m')
df_res['lvl'] = pd.to_numeric(df_res['lvl'], errors='coerce').fillna(0)

# ────────────────────────────────────────────────────────────────
# Filters
# ────────────────────────────────────────────────────────────────
st.subheader("Filters")

col1, col2, col3 = st.columns(3)
with col1:
    if not df_monthly.empty:
        months = sorted(df_monthly.index.astype(str).unique())
        selected_month = st.selectbox("Select Month", months, index=len(months)-1 if months else 0)
    else:
        selected_month = None

with col2:
    cities = ["All"] + sorted(df_res['city_name'].dropna().unique().tolist())
    selected_city = st.selectbox("City", cities)

with col3:
    cuisines = ["All"] + sorted(df_res['res_cuisine_new'].dropna().unique().tolist())
    selected_cuisine = st.selectbox("Cuisine", cuisines)

# ────────────────────────────────────────────────────────────────
# Portfolio KPIs – Latest month
# ────────────────────────────────────────────────────────────────
if not df_monthly.empty:
    latest_row = df_monthly.iloc[-1]

    st.subheader("Portfolio Summary – Latest Month")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Orders", f"{int(latest_row.get('Orders_Total_OV', 0)):,}")
    k2.metric("GMV", f"₹{int(latest_row.get('Revenue_GMV', 0)):,}")
    k3.metric("AOV", f"₹{int(latest_row.get('Revenue_AOV', 0)):,}")
    k4.metric("Ads ROI", latest_row.get('Advertisement_Ads ROI', 'N/A'))
    k5.metric("Organic Orders %", latest_row.get('Organic _Organic Orders%', 'N/A'))

# ────────────────────────────────────────────────────────────────
# Charts
# ────────────────────────────────────────────────────────────────
if not df_monthly.empty:
    st.subheader("MoM Trends")

    c1, c2 = st.columns(2)

    with c1:
        order_cols = [c for c in df_monthly.columns if 'Orders' in c]
        if order_cols:
            fig_orders = px.line(
                df_monthly,
                x=df_monthly.index,
                y=order_cols[:3],  # limit to first 3 to avoid clutter
                title="Orders Trend",
                markers=True
            )
            st.plotly_chart(fig_orders, use_container_width=True)

    with c2:
        revenue_cols = [c for c in df_monthly.columns if 'GMV' in c or 'CV' in c]
        if revenue_cols:
            fig_revenue = px.bar(
                df_monthly,
                x=df_monthly.index,
                y=revenue_cols,
                barmode='group',
                title="GMV & CV Trend"
            )
            st.plotly_chart(fig_revenue, use_container_width=True)

# ────────────────────────────────────────────────────────────────
# Filtered Restaurant Table
# ────────────────────────────────────────────────────────────────
st.subheader("Restaurant Performance")

filtered_res = df_res.copy()

if selected_city != "All":
    filtered_res = filtered_res[filtered_res['city_name'] == selected_city]

if selected_cuisine != "All":
    filtered_res = filtered_res[filtered_res['res_cuisine_new'] == selected_cuisine]

if selected_month:
    filtered_res = filtered_res[filtered_res['Month'] == selected_month]

st.dataframe(
    filtered_res[['Month', 'city_name', 'res_name', 'res_cuisine_new', 'lvl']]
    .sort_values('lvl', ascending=False),
    use_container_width=True,
    hide_index=True
)

# ────────────────────────────────────────────────────────────────
# Download section
# ────────────────────────────────────────────────────────────────
st.subheader("Export")

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="📥 Monthly Portfolio CSV",
        data=df_monthly.to_csv().encode('utf-8'),
        file_name="portfolio_monthly.csv",
        mime="text/csv"
    )

with col2:
    st.download_button(
        label="📥 Restaurants MoM CSV",
        data=df_res.to_csv(index=False).encode('utf-8'),
        file_name="restaurants_mom.csv",
        mime="text/csv"
    )

st.caption("Dashboard v2 – fixed column renaming error | March 2026")
