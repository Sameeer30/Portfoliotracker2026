import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Ajmer Portfolio • 2026",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    .big-metric {font-size: 2.8rem; font-weight: 700; margin: 0;}
    .card {background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);}
    .flag-green {color: #10b981; font-size: 1.4rem; font-weight: bold;}
    .flag-red   {color: #ef4444; font-size: 1.4rem; font-weight: bold;}
    .hero {background: linear-gradient(90deg, #1e40af, #3b82f6); padding: 30px; border-radius: 20px; color: white; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1 style="margin:0;">📊 Ajmer Restaurant Portfolio • Live Tracker</h1>'
    '<p style="opacity:0.9; margin-top:8px;">Restaurant-wise & Month-wise Performance • March 2026</p></div>',
    unsafe_allow_html=True
)

# ── Upload ──────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload Res_level_txn CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()

    # ── Core calculations ─────────────────────────────────────────────
    df['Month']       = df['Aggregation']
    df['Orders']      = df['delivered_ov'].fillna(0)
    df['CV']          = df['cv'].fillna(0)
    df['GMV']         = df['GMV'].fillna(0)
    df['AOV']         = df.apply(lambda x: round(x['GMV']/x['Orders'],1) if x['Orders']>0 else 0, axis=1)
    df['SL_pct']      = df.apply(lambda x: round(x['Orders']/x['Total_ov']*100,1) if x['Total_ov']>0 else 0, axis=1)

    df['Ads_Booked']  = df['booked_amount'].fillna(0)
    df['Ads_Billed']  = df['billed_amount'].fillna(0)
    df['Ads_CV_pct']  = df.apply(lambda x: round(x['ads_cv']/x['CV']*100,1) if x['CV']>0 else 0, axis=1)

    df['ZVD'] = df.get('zvd', 0).fillna(0)
    df['MVD'] = df.get('mvd', 0).fillna(0)

    # Sort months for dropdown
    all_months = sorted(df['Month'].unique())
    month_options = ["All"] + all_months

    # ── Sidebar filters ─────────────────────────────────────────────────
    st.sidebar.header("🎛️ Filters")

    selected_res = st.sidebar.selectbox(
        "Restaurant Name",
        options=["All"] + sorted(df['res_name'].unique()),
        index=0
    )

    selected_month = st.sidebar.selectbox(
        "Month",
        options=month_options,
        index=len(month_options)-1   # default = latest month
    )

    rank_by = st.sidebar.selectbox(
        "Rank / Sort by",
        options=[
            "GMV (highest first)",
            "Orders (highest first)",
            "AOV (highest first)",
            "CV (highest first)",
            "Ads/CV % (highest first)",
            "Ads Booked (highest first)",
            "SL % (highest first)",
            "ZVD (highest first)",
            "MVD (highest first)",
            "Name (A-Z)",
        ],
        index=0
    )

    sort_map = {
        "GMV (highest first)":            ("GMV", False),
        "Orders (highest first)":          ("Orders", False),
        "AOV (highest first)":             ("AOV", False),
        "CV (highest first)":              ("CV", False),
        "Ads/CV % (highest first)":        ("Ads_CV_pct", False),
        "Ads Booked (highest first)":      ("Ads_Booked", False),
        "SL % (highest first)":            ("SL_pct", False),
        "ZVD (highest first)":             ("ZVD", False),
        "MVD (highest first)":             ("MVD", False),
        "Name (A-Z)":                      ("res_name", True),
    }
    sort_col, ascending = sort_map[rank_by]

    # ── Apply filters ───────────────────────────────────────────────────
    filtered = df.copy()

    if selected_res != "All":
        filtered = filtered[filtered['res_name'] == selected_res]

    if selected_month != "All":
        filtered = filtered[filtered['Month'] == selected_month]

    view_df = filtered.sort_values(sort_col, ascending=ascending)

    # ── KPI Cards (latest data or filtered view) ────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f'<div class="card"><h3>Restaurants Shown</h3>'
            f'<span class="big-metric">{len(view_df["res_name"].unique())}</span></div>',
            unsafe_allow_html=True
        )

    with col2:
        gmv_val = view_df['GMV'].sum() / 1_00_000
        st.metric("Total GMV", f"₹{gmv_val:,.1f} L")

    with col3:
        orders_val = int(view_df['Orders'].sum())
        st.metric("Total Orders", f"{orders_val:,}")

    with col4:
        aov_val = round(view_df['AOV'].mean(), 1) if not view_df.empty else 0
        st.metric("Avg AOV", f"₹{aov_val}")

    with col5:
        ads_eff = round(view_df['Ads_CV_pct'].mean(), 1) if not view_df.empty else 0
        st.metric("Ad Contribution", f"{ads_eff}%")

    # ── Main table ──────────────────────────────────────────────────────
    title_prefix = f"{selected_res} – " if selected_res != "All" else ""
    month_text = selected_month if selected_month != "All" else "All Months"

    st.subheader(f"{title_prefix}Performance {month_text} – sorted by {rank_by}")

    styled = view_df[['res_name', 'Month', 'res_cuisine_new', 'Orders', 'GMV', 'AOV', 'CV',
                      'SL_pct', 'Ads_CV_pct', 'Ads_Booked', 'ZVD', 'MVD']]\
             .style.format({
                 'GMV': '₹{:,.0f}',
                 'CV': '₹{:,.0f}',
                 'AOV': '₹{:.1f}',
                 'Ads_Booked': '₹{:,.0f}',
                 'Ads_CV_pct': '{:.1f}%',
                 'SL_pct': '{:.1f}%',
                 'ZVD': '{:,.0f}',
                 'MVD': '{:,.0f}',
             })\
             .highlight_max(subset=['GMV', 'Orders', 'CV'], color='#d4edda')\
             .highlight_min(subset=['SL_pct'], color='#f8d7da')\
             .highlight_max(subset=['Ads_CV_pct'], color='#fff3cd')

    st.dataframe(styled, use_container_width=True, height=500)

    # ── Deep dive (only when single restaurant selected) ────────────────
    if selected_res != "All":
        st.subheader(f"🔍 History of {selected_res}")

        res_data = df[df['res_name'] == selected_res].sort_values('Month')

        fig_res = px.line(
            res_data,
            x='Month',
            y=['GMV', 'Orders', 'CV', 'Ads_Booked'],
            markers=True,
            title=f"{selected_res} – GMV, Orders, CV & Ads Booked Trend",
            color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
        )
        st.plotly_chart(fig_res, use_container_width=True)

        # Latest status flag
        last = res_data.iloc[-1]
        prev = res_data.iloc[-2] if len(res_data) > 1 else None
        change = (last['GMV'] - prev['GMV']) / prev['GMV'] * 100 if prev is not None and prev['GMV'] > 0 else 0

        flag = "🟢 STRONG GROWTH" if change > 25 else "🔴 ATTENTION NEEDED" if change < -25 else "🟡 STABLE"
        flag_color = "#10b981" if change > 25 else "#ef4444" if change < -25 else "#eab308"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);padding:20px;border-radius:16px;color:white;">
            <h3>Latest Status ({last['Month']})</h3>
            <p style="color:{flag_color}; font-size:1.6rem; margin:12px 0;">{flag}</p>
            <p><strong>GMV:</strong> ₹{last['GMV']:,.0f} | 
               <strong>Orders:</strong> {int(last['Orders'])} | 
               <strong>AOV:</strong> ₹{last['AOV']:.1f} | 
               <strong>Ads/CV:</strong> {last['Ads_CV_pct']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Download ────────────────────────────────────────────────────────
    st.download_button(
        "📥 Download Filtered Data",
        data=view_df.to_csv(index=False).encode(),
        file_name=f"Ajmer_{selected_res.replace(' ','_')}_{selected_month}.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Upload your CSV file to start exploring restaurant & month-wise performance")

st.caption("Dashboard • Restaurant + Month focus • Raja's Portfolio Tracker • 2026")
