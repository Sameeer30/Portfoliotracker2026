import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Ajmer Portfolio • 2026", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# ── Custom CSS for premium look ─────────────────────────────────────
st.markdown("""
<style>
    .big-metric {font-size: 2.8rem; font-weight: 700; margin: 0;}
    .card {background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);}
    .flag-green {color: #10b981; font-size: 1.4rem;}
    .flag-red   {color: #ef4444; font-size: 1.4rem;}
    .hero {background: linear-gradient(90deg, #1e40af, #3b82f6); padding: 30px; border-radius: 20px; color: white;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1 style="margin:0; text-align:center;">📊 Ajmer Restaurant Portfolio • Live Tracker</h1><p style="text-align:center; opacity:0.9;">March 2026 • Smart Insights • Beautifully Designed</p></div>', unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload latest Res_level_txn CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()

    # Core + Ads calculations
    df['Month'] = df['Aggregation']
    df['Orders'] = df['delivered_ov'].fillna(0)
    df['CV'] = df['cv'].fillna(0)
    df['GMV'] = df['GMV'].fillna(0)
    df['AOV'] = df.apply(lambda x: round(x['GMV']/x['Orders'],1) if x['Orders']>0 else 0, axis=1)
    df['SL_pct'] = df.apply(lambda x: round(x['Orders']/x['Total_ov']*100,1) if x['Total_ov']>0 else 0, axis=1)
    
    df['Ads_Booked'] = df['booked_amount'].fillna(0)
    df['Ads_Billed'] = df['billed_amount'].fillna(0)
    df['Ads_CV_pct'] = df.apply(lambda x: round(x['ads_cv']/x['CV']*100,1) if x['CV']>0 else 0, axis=1)

    latest = df['Month'].max()
    prev = sorted(df['Month'].unique())[-2] if len(df['Month'].unique()) >= 2 else None

    # ── Sidebar Filters ─────────────────────────────────────────────
    st.sidebar.header("🎛️ Filters")
    cuisine_filter = st.sidebar.multiselect("Cuisine", options=df['res_cuisine_new'].dropna().unique(), default=None)
    month_filter = st.sidebar.selectbox("View Month", options=sorted(df['Month'].unique()), index=len(df['Month'].unique())-1)

    filtered = df[df['Month'] == month_filter]
    if cuisine_filter:
        filtered = filtered[filtered['res_cuisine_new'].isin(cuisine_filter)]

    # ── KPI Cards (Beautiful gradient) ─────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown('<div class="card"><h3>Active Restaurants</h3><span class="big-metric">' + str(len(filtered['res_name'].unique())) + '</span></div>', unsafe_allow_html=True)
    
    with col2:
        gmv_val = filtered['GMV'].sum() / 1_00_000
        st.metric("Total GMV", f"₹{gmv_val:,.1f}L", delta=None)

    with col3:
        orders_val = int(filtered['Orders'].sum())
        st.metric("Total Orders", f"{orders_val:,}")

    with col4:
        aov_val = round(filtered['AOV'].mean(), 1)
        st.metric("Avg AOV", f"₹{aov_val}")

    with col5:
        ads_eff = round(filtered['Ads_CV_pct'].mean(), 1)
        st.metric("Ad Contribution", f"{ads_eff}%")

    # ── Growth Radar + Flags ───────────────────────────────────────
    st.subheader("🚀 Growth Radar & Smart Flags")

    if prev:
        prev_df = df[df['Month'] == prev]
        mom = filtered.groupby('res_name').agg({'GMV':'sum','Orders':'sum'}).reset_index()
        mom_prev = prev_df.groupby('res_name').agg({'GMV':'sum','Orders':'sum'}).reset_index()
        mom = mom.merge(mom_prev, on='res_name', suffixes=('_now','_prev'), how='left').fillna(0)
        mom['GMV_Change_%'] = mom.apply(lambda x: round((x['GMV_now']-x['GMV_prev'])/x['GMV_prev']*100,1) if x['GMV_prev']>0 else 0, axis=1)

        # Top risers & fallers
        risers = mom.nlargest(5, 'GMV_Change_%')
        fallers = mom.nsmallest(5, 'GMV_Change_%')

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🟢 Top Risers**")
            for _, r in risers.iterrows():
                st.success(f"**{r['res_name']}** ↑ {r['GMV_Change_%']}%")
        with c2:
            st.markdown("**🔴 Top Fallers / Risk**")
            for _, r in fallers.iterrows():
                if r['GMV_Change_%'] <= -25:
                    st.error(f"**{r['res_name']}** ↓ {r['GMV_Change_%']}%")
                else:
                    st.warning(f"{r['res_name']} ↓ {r['GMV_Change_%']}%")

    # ── Beautiful Charts ───────────────────────────────────────────
    st.subheader("Visual Insights")

    c1, c2 = st.columns(2)
    with c1:
        top10 = filtered.nlargest(10, 'GMV')
        fig = px.bar(top10, x='GMV', y='res_name', orientation='h', text='GMV',
                     title="Top 10 Restaurants by GMV", color='GMV',
                     color_continuous_scale='emerald')
        fig.update_traces(texttemplate='₹%{x:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cuisine_pie = filtered.groupby('res_cuisine_new')['GMV'].sum().reset_index()
        fig_pie = px.pie(cuisine_pie, names='res_cuisine_new', values='GMV', title="Cuisine Contribution",
                         color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Restaurant Deep Dive (Premium Card Style) ───────────────────
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
            <h3 style="color:{flag_color}; font-size:2rem;">{flag}</h3>
            <p><strong>Latest GMV:</strong> ₹{last['GMV']:,.0f} | 
               <strong>Orders:</strong> {int(last['Orders'])} | 
               <strong>AOV:</strong> ₹{last['AOV']:.0f}</p>
        </div>
        """, unsafe_allow_html=True)

        # Trend chart
        fig_res = px.line(res_data, x='Month', y=['GMV','Orders'], markers=True,
                          title=f"{selected} Performance Trend",
                          color_discrete_sequence=['#3b82f6', '#10b981'])
        st.plotly_chart(fig_res, use_container_width=True)

    # ── Download ───────────────────────────────────────────────────
    st.download_button("📥 Download Complete Report", 
                       data=df.to_csv(index=False).encode(),
                       file_name=f"Ajmer_Portfolio_Full_Report_{latest}.csv",
                       mime="text/csv")

else:
    st.info("👆 Upload your CSV to unlock the beautiful dashboard")

st.caption("Built with ❤️ for Raja • Modern cards • Smart flags • Premium visuals")
