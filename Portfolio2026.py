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

# ── Custom CSS for better appearance ────────────────────────────────
st.markdown("""
<style>
    .big-metric {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
    }
    .card {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .flag-green { color: #10b981; font-size: 1.4rem; font-weight: bold; }
    .flag-red   { color: #ef4444; font-size: 1.4rem; font-weight: bold; }
    .hero {
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1 style="margin:0;">📊 Ajmer Restaurant Portfolio • Live Tracker</h1>'
    '<p style="opacity:0.9; margin-top:8px;">March 2026 • Smart Insights • Clean Design</p></div>',
    unsafe_allow_html=True
)

# ── File upload ─────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload latest Res_level_txn CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()

    # ── Core calculations ───────────────────────────────────────────
    df['Month']       = df['Aggregation']
    df['Orders']      = df['delivered_ov'].fillna(0)
    df['CV']          = df['cv'].fillna(0)
    df['GMV']         = df['GMV'].fillna(0)
    df['AOV']         = df.apply(lambda x: round(x['GMV']/x['Orders'], 1) if x['Orders'] > 0 else 0, axis=1)
    df['SL_pct']      = df.apply(lambda x: round(x['Orders']/x['Total_ov']*100, 1) if x['Total_ov'] > 0 else 0, axis=1)

    df['Ads_Booked']  = df['booked_amount'].fillna(0)
    df['Ads_Billed']  = df['billed_amount'].fillna(0)
    df['Ads_CV_pct']  = df.apply(lambda x: round(x['ads_cv']/x['CV']*100, 1) if x['CV'] > 0 else 0, axis=1)

    # ZVD / MVD fallback
    df['ZVD'] = df.get('zvd', 0).fillna(0)
    df['MVD'] = df.get('mvd', 0).fillna(0)

    latest = df['Month'].max()
    prev = sorted(df['Month'].unique())[-2] if len(df['Month'].unique()) >= 2 else None

    # ── Sidebar controls ────────────────────────────────────────────
    st.sidebar.header("🎛️ Controls")

    cuisine_filter = st.sidebar.multiselect(
        "Cuisine",
        options=sorted(df['res_cuisine_new'].dropna().unique()),
        default=[]
    )

    rank_by = st.sidebar.selectbox(
        "Rank / Sort restaurants by",
        options=[
            "GMV (highest first)",
            "Orders (highest first)",
            "AOV (highest first)",
            "CV (highest first)",
            "Ads/CV % (highest first)",
            "Ads Booked (highest first)",
            "SL % (highest first)",
            "ZVD (highest first – attention)",
            "MVD (highest first – attention)",
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
        "ZVD (highest first – attention)": ("ZVD", False),
        "MVD (highest first – attention)": ("MVD", False),
        "Name (A-Z)":                      ("res_name", True),
    }

    sort_col, ascending = sort_map[rank_by]

    # ── Apply filters & sorting ─────────────────────────────────────
    filtered = df[df['Month'] == latest].copy()
    if cuisine_filter:
        filtered = filtered[filtered['res_cuisine_new'].isin(cuisine_filter)]

    view_df = filtered.sort_values(sort_col, ascending=ascending)

    # ── KPI Cards ───────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f'<div class="card"><h3>Active Restaurants</h3>'
            f'<span class="big-metric">{len(filtered["res_name"].unique())}</span></div>',
            unsafe_allow_html=True
        )

    with col2:
        gmv_val = filtered['GMV'].sum() / 1_00_000
        st.metric("Total GMV", f"₹{gmv_val:,.1f} L")

    with col3:
        orders_val = int(filtered['Orders'].sum())
        st.metric("Total Orders", f"{orders_val:,}")

    with col4:
        aov_val = round(filtered['AOV'].mean(), 1)
        st.metric("Avg AOV", f"₹{aov_val}")

    with col5:
        ads_eff = round(filtered['Ads_CV_pct'].mean(), 1)
        st.metric("Ad Contribution", f"{ads_eff}%")

    # ── Ranked / Sorted list ────────────────────────────────────────
    st.subheader(f"Restaurants ranked by → {rank_by}")

    styled_df = view_df[['res_name', 'res_cuisine_new', 'Orders', 'GMV', 'AOV', 'CV',
                         'SL_pct', 'Ads_CV_pct', 'Ads_Booked', 'ZVD', 'MVD']]\
                .head(40)\
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

    st.dataframe(styled_df, use_container_width=True)

    # ── Charts ──────────────────────────────────────────────────────
    st.subheader("Visual Insights")

    c1, c2 = st.columns(2)

    with c1:
        top10 = filtered.nlargest(10, 'GMV')
        fig = px.bar(
            top10,
            x='GMV',
            y='res_name',
            orientation='h',
            text='GMV',
            title="Top 10 Restaurants by GMV",
            color='GMV',
            color_continuous_scale='greens'
        )
        fig.update_traces(texttemplate='₹%{x:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cuisine_pie = filtered.groupby('res_cuisine_new')['GMV'].sum().reset_index()
        fig_pie = px.pie(
            cuisine_pie,
            names='res_cuisine_new',
            values='GMV',
            title="Cuisine Contribution",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Restaurant Deep Dive ────────────────────────────────────────
    st.subheader("🔍 Restaurant Deep Dive")
    selected = st.selectbox("Choose a restaurant", options=sorted(df['res_name'].unique()))

    if selected:
        res_data = df[df['res_name'] == selected].sort_values('Month')
        last = res_data.iloc[-1]
        prev = res_data.iloc[-2] if len(res_data) > 1 else None

        change = (last['GMV'] - prev['GMV']) / prev['GMV'] * 100 if prev is not None and prev['GMV'] > 0 else 0

        flag = "🟢 STRONG GROWTH" if change > 25 else "🔴 ATTENTION NEEDED" if change < -25 else "🟡 STABLE"
        flag_color = "#10b981" if change > 25 else "#ef4444" if change < -25 else "#eab308"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);padding:25px;border-radius:20px;color:white;">
            <h2>{selected}</h2>
            <h3 style="color:{flag_color};">{flag}</h3>
            <p><strong>Latest GMV:</strong> ₹{last['GMV']:,.0f} | 
               <strong>Orders:</strong> {int(last['Orders'])} | 
               <strong>AOV:</strong> ₹{last['AOV']:.0f}</p>
        </div>
        """, unsafe_allow_html=True)

        fig_res = px.line(
            res_data,
            x='Month',
            y=['GMV', 'Orders'],
            markers=True,
            title=f"{selected} Performance Trend",
            color_discrete_sequence=['#3b82f6', '#10b981']
        )
        st.plotly_chart(fig_res, use_container_width=True)

    # ── Download ────────────────────────────────────────────────────
    st.download_button(
        "📥 Download Full Report",
        data=df.to_csv(index=False).encode(),
        file_name=f"Ajmer_Portfolio_Full_{latest}.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Upload your CSV file to unlock the dashboard")

st.caption("Dashboard • Modern UI • Safe styling • Raja's Portfolio Tracker • March 2026")
