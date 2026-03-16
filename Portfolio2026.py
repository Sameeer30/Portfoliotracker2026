import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="3D Portfolio Tracker", layout="wide", page_icon="📈")

# ── Modern CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
    .header {background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 25px; border-radius: 20px; color: white; text-align: center;}
    .card {background: linear-gradient(135deg, #1e2937, #334155); color: white; padding: 18px; border-radius: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.3);}
    .suggestion-green {background: #052e16; border-left: 6px solid #10b981; padding: 12px; border-radius: 8px; margin: 8px 0;}
    .suggestion-red   {background: #450a0a; border-left: 6px solid #ef4444; padding: 12px; border-radius: 8px; margin: 8px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>📊 3D Portfolio Tracker — Ajmer Restaurants</h1><p>Interactive • Smart Suggestions • March 2026</p></div>', unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload your Res_level_txn CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()

    # ── Calculate Metrics ─────────────────────────────────────────────
    df['Month']      = df['Aggregation']
    df['Orders']     = df['delivered_ov'].fillna(0)
    df['CV']         = df['cv'].fillna(0)
    df['GMV']        = df['GMV'].fillna(0)
    df['AOV']        = df.apply(lambda x: round(x['GMV']/x['Orders'],1) if x['Orders']>0 else 0, axis=1)
    df['SL_pct']     = df.apply(lambda x: round(x['Orders']/x['Total_ov']*100,1) if x['Total_ov']>0 else 0, axis=1)
    df['Ads_CV_pct'] = df.apply(lambda x: round(x['ads_cv']/x['CV']*100,1) if x['CV']>0 else 0, axis=1)
    df['ZVD']        = df.get('zvd', 0).fillna(0)
    df['MVD']        = df.get('mvd', 0).fillna(0)

    latest_month = df['Month'].max()
    all_months = ["All"] + sorted(df['Month'].unique())

    # ── Sidebar ───────────────────────────────────────────────────────
    st.sidebar.header("Filters")
    view_mode = st.sidebar.radio("Select View", ["📊 Portfolio 3D Overview", "🔍 Restaurant-wise Details"], index=0)

    selected_month = st.sidebar.selectbox("Month", all_months, index=len(all_months)-1)
    selected_res = st.sidebar.selectbox("Restaurant", options=["All"] + sorted(df['res_name'].unique()))

    # Filter data
    filtered = df.copy()
    if selected_month != "All":
        filtered = filtered[filtered['Month'] == selected_month]
    if selected_res != "All":
        filtered = filtered[filtered['res_name'] == selected_res]

    # ── VIEW 1: Portfolio 3D Overview ──────────────────────────────────
    if view_mode == "📊 Portfolio 3D Overview":
        st.subheader("Portfolio 3D Tracker (GMV × Orders × SL%)")

        fig_3d = px.scatter_3d(
            filtered,
            x='GMV',
            y='Orders',
            z='SL_pct',
            size='AOV',
            color='Ads_CV_pct',
            hover_name='res_name',
            text='res_name',
            color_continuous_scale='RdYlGn',
            title="3D Performance View • Bubble size = AOV • Color = Ad Contribution %",
            labels={'GMV':'GMV (₹)', 'Orders':'Orders', 'SL_pct':'Service Level %'}
        )
        fig_3d.update_traces(marker=dict(sizemin=8, sizeref=0.1))
        st.plotly_chart(fig_3d, use_container_width=True)

        # Portfolio Summary Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total GMV", f"₹{filtered['GMV'].sum()/1e5:,.1f} L")
        col2.metric("Total Orders", f"{int(filtered['Orders'].sum()):,}")
        col3.metric("Avg AOV", f"₹{filtered['AOV'].mean():.0f}")
        col4.metric("Avg Ad Contribution", f"{filtered['Ads_CV_pct'].mean():.1f}%")

        # Portfolio-level Suggestions
        st.subheader("💡 Portfolio Recommendations")
        total_res = len(filtered['res_name'].unique())
        zero_order = len(filtered[filtered['Orders'] == 0])
        low_sl = len(filtered[filtered['SL_pct'] < 85])

        if zero_order > total_res * 0.15:
            st.markdown('<div class="suggestion-red"><strong>🔴 Critical:</strong> ' + str(zero_order) + ' restaurants have zero orders this month → urgent reactivation needed.</div>', unsafe_allow_html=True)
        if low_sl > total_res * 0.20:
            st.markdown('<div class="suggestion-red"><strong>🔴 Critical:</strong> ' + str(low_sl) + ' restaurants have SL% < 85% → delivery operations review required.</div>', unsafe_allow_html=True)
        if filtered['Ads_CV_pct'].mean() < 12:
            st.markdown('<div class="suggestion-red"><strong>🔴 Opportunity:</strong> Ad contribution is low → test higher budgets on top 10 GMV restaurants.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="suggestion-green"><strong>🟢 Good sign:</strong> Ad contribution is healthy — continue scaling winning campaigns.</div>', unsafe_allow_html=True)

    # ── VIEW 2: Restaurant-wise Details ────────────────────────────────
    else:
        st.subheader("Restaurant-wise Performance Details")

        if selected_res == "All":
            st.info("Please select a specific restaurant from the sidebar to see detailed view")
        else:
            res_df = df[df['res_name'] == selected_res].sort_values('Month')

            # Detailed table
            st.dataframe(
                res_df[['Month', 'Orders', 'GMV', 'AOV', 'CV', 'SL_pct', 'Ads_CV_pct', 'ZVD', 'MVD']]
                .style.format({
                    'GMV': '₹{:,.0f}',
                    'CV': '₹{:,.0f}',
                    'AOV': '₹{:.1f}',
                    'Ads_CV_pct': '{:.1f}%',
                    'SL_pct': '{:.1f}%',
                    'ZVD': '{:,.0f}',
                    'MVD': '{:,.0f}',
                })
                .highlight_max(subset=['GMV', 'Orders', 'CV'], color='#d4edda')
                .highlight_min(subset=['SL_pct'], color='#f8d7da'),
                use_container_width=True
            )

            # Trend chart
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=res_df['Month'], y=res_df['GMV'], name='GMV', yaxis='y'))
            fig_trend.add_trace(go.Scatter(x=res_df['Month'], y=res_df['Orders'], name='Orders', yaxis='y2'))
            fig_trend.update_layout(
                title=f"{selected_res} — Month-on-Month Trend",
                yaxis=dict(title='GMV (₹)'),
                yaxis2=dict(title='Orders', overlaying='y', side='right')
            )
            st.plotly_chart(fig_trend, use_container_width=True)

            # Restaurant-specific Suggestions
            st.subheader(f"💡 Recommendations for {selected_res}")
            latest = res_df.iloc[-1]
            prev = res_df.iloc[-2] if len(res_df) > 1 else None
            gmv_change = (latest['GMV'] - prev['GMV']) / prev['GMV'] * 100 if prev is not None and prev['GMV'] > 0 else 0

            if latest['SL_pct'] < 85:
                st.markdown('<div class="suggestion-red"><strong>🔴 Urgent:</strong> Service Level is low — focus on delivery partner availability & order acceptance.</div>', unsafe_allow_html=True)
            if latest['Ads_CV_pct'] < 8:
                st.markdown('<div class="suggestion-red"><strong>🔴 Action:</strong> Ad contribution too low — increase budget or refine targeting.</div>', unsafe_allow_html=True)
            if latest['ZVD'] > 5000 or latest['MVD'] > 5000:
                st.markdown('<div class="suggestion-red"><strong>🔴 Critical:</strong> High ZVD/MVD values detected — check supply chain & menu pricing.</div>', unsafe_allow_html=True)
            if gmv_change > 20:
                st.markdown('<div class="suggestion-green"><strong>🟢 Excellent:</strong> Strong month-on-month growth — consider menu expansion or promotions.</div>', unsafe_allow_html=True)
            if gmv_change < -20:
                st.markdown('<div class="suggestion-red"><strong>🔴 Alert:</strong> Significant GMV drop — review pricing, competition & customer feedback.</div>', unsafe_allow_html=True)

    # ── Download ────────────────────────────────────────────────────────
    st.download_button(
        "📥 Download Filtered Data",
        data=filtered.to_csv(index=False).encode(),
        file_name=f"Portfolio_{selected_month}_{selected_res.replace(' ','_')}.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Upload your CSV file to activate the interactive 3D tracker")

st.caption("3D Portfolio Tracker • Built fresh • Sameer's Ajmer Restaurants • March 2026")
