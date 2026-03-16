import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Portfolio Tracker - Ajmer", layout="wide", page_icon="📊")

# ── Modern styling ─────────────────────────────────────────────────────
st.markdown("""
<style>
    .header {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        padding: 25px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 24px;
    }
    .card {
        background: #1e293b;
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        margin-bottom: 16px;
    }
    .attention-box {
        background: #450a0a;
        border-left: 6px solid #ef4444;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    .good-box {
        background: #052e16;
        border-left: 6px solid #10b981;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    .metric-label {font-size: 1.1rem; opacity: 0.9;}
    .metric-value {font-size: 2.4rem; font-weight: 700;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="header"><h1>📊 Ajmer Restaurant Portfolio Tracker</h1>'
    '<p>Detailed Overview • Attention Flags • Smart Suggestions • March 2026</p></div>',
    unsafe_allow_html=True
)

# ── Upload ─────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload Res_level_txn CSV file", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()

    # ── Core metrics ────────────────────────────────────────────────────
    df['Month']      = df['Aggregation']
    df['Orders']     = df['delivered_ov'].fillna(0)
    df['CV']         = df['cv'].fillna(0)
    df['GMV']        = df['GMV'].fillna(0)
    df['AOV']        = df.apply(lambda x: round(x['GMV']/x['Orders'],1) if x['Orders']>0 else 0, axis=1)
    df['SL_pct']     = df.apply(lambda x: round(x['Orders']/x['Total_ov']*100,1) if x['Total_ov']>0 else 0, axis=1)
    df['Ads_CV_pct'] = df.apply(lambda x: round(x['ads_cv']/x['CV']*100,1) if x['CV']>0 else 0, axis=1)
    df['ZVD']        = df.get('zvd', 0).fillna(0)
    df['MVD']        = df.get('mvd', 0).fillna(0)

    # Available months
    months = ["All"] + sorted(df['Month'].unique())

    # ── Sidebar filters ─────────────────────────────────────────────────
    st.sidebar.header("Filters & Controls")
    selected_month = st.sidebar.selectbox("Month", months, index=len(months)-1)
    selected_res   = st.sidebar.selectbox("Restaurant (optional)", ["All"] + sorted(df['res_name'].unique()))

    # Apply filters
    filtered = df.copy()
    if selected_month != "All":
        filtered = filtered[filtered['Month'] == selected_month]
    if selected_res != "All":
        filtered = filtered[filtered['res_name'] == selected_res]

    # Reference month for zero-order flagging
    reference_month = selected_month if selected_month != "All" else df['Month'].max()

    # ── Portfolio Summary Cards ─────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown('<div class="card"><div class="metric-label">Active Restaurants</div><div class="metric-value">' + str(len(filtered['res_name'].unique())) + '</div></div>', unsafe_allow_html=True)
    col2.metric("Total GMV", f"₹{filtered['GMV'].sum()/1e5:,.1f} L" if not filtered.empty else "₹0")
    col3.metric("Total Orders", f"{int(filtered['Orders'].sum()):,}" if not filtered.empty else "0")
    col4.metric("Avg AOV", f"₹{filtered['AOV'].mean():.0f}" if not filtered.empty else "₹0")
    col5.metric("Avg Ad Contribution", f"{filtered['Ads_CV_pct'].mean():.1f}%" if not filtered.empty else "0.0%")

    # ── Attention Needed Section ───────────────────────────────────────
    st.subheader("🚨 Attention Needed – Restaurants Requiring Action")

    attention = []
    for _, row in filtered.iterrows():
        issues = []

        if row['Orders'] == 0 and row['Month'] == reference_month:
            issues.append("Zero orders in current view month")

        if row['SL_pct'] < 85:
            issues.append(f"Low SL% ({row['SL_pct']:.1f}%)")

        if row['ZVD'] > 5000 or row['MVD'] > 5000:
            issues.append(f"High ZVD/MVD (₹{row['ZVD']:,.0f} / ₹{row['MVD']:,.0f})")

        if row['Ads_CV_pct'] < 8:
            issues.append(f"Low ad contribution ({row['Ads_CV_pct']:.1f}%)")

        if issues:
            attention.append({
                'Restaurant': row['res_name'],
                'Month': row['Month'],
                'Issues': " • ".join(issues),
                'GMV': row['GMV'],
                'Orders': row['Orders'],
                'SL%': row['SL_pct'],
                'Ads%': row['Ads_CV_pct']
            })

    if attention:
        att_df = pd.DataFrame(attention).sort_values('GMV', ascending=False)

        st.dataframe(
            att_df.style.format({
                'GMV': '₹{:,.0f}',
                'SL%': '{:.1f}%',
                'Ads%': '{:.1f}%'
            })
            .highlight_max(subset=['GMV'], color='#7f1d1d')     # dark red for high GMV in attention list
            .highlight_min(subset=['SL%'], color='#7f1d1d'),    # dark red for low SL
            use_container_width=True
        )

        st.markdown('<div class="attention-box"><strong>Quick Actions:</strong></div>', unsafe_allow_html=True)

        for _, r in att_df.iterrows():
            st.markdown(f"**{r['Restaurant']}** ({r['Month']}) – {r['Issues']}")
    else:
        st.markdown('<div class="good-box"><strong>🟢 All good!</strong> No restaurants currently require urgent attention in the selected view.</div>', unsafe_allow_html=True)

    # ── Detailed Portfolio Table ───────────────────────────────────────
    st.subheader("Detailed Portfolio View")

    display_cols = ['res_name', 'Month', 'Orders', 'GMV', 'AOV', 'CV', 'SL_pct', 'Ads_CV_pct', 'ZVD', 'MVD']

    styled_table = filtered[display_cols].sort_values('GMV', ascending=False).style.format({
        'GMV': '₹{:,.0f}',
        'CV': '₹{:,.0f}',
        'AOV': '₹{:.1f}',
        'Ads_CV_pct': '{:.1f}%',
        'SL_pct': '{:.1f}%',
        'ZVD': '{:,.0f}',
        'MVD': '{:,.0f}',
    }).highlight_max(subset=['GMV', 'Orders', 'CV'], color='#d4edda')\
      .highlight_min(subset=['SL_pct'], color='#f8d7da')\
      .highlight_max(subset=['Ads_CV_pct'], color='#fff3cd')

    st.dataframe(styled_table, use_container_width=True, height=550)

    # ── Visuals ─────────────────────────────────────────────────────────
    st.subheader("Visual Insights")

    c1, c2 = st.columns(2)

    with c1:
        fig_bar = px.bar(
            filtered.nlargest(12, 'GMV'),
            x='GMV',
            y='res_name',
            orientation='h',
            text='GMV',
            title="Top 12 Restaurants by GMV",
            color='SL_pct',
            color_continuous_scale='RdYlGn'
        )
        fig_bar.update_traces(texttemplate='₹%{x:,.0f}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        fig_pie = px.pie(
            filtered.groupby('res_cuisine_new')['GMV'].sum().reset_index(),
            names='res_cuisine_new',
            values='GMV',
            title="GMV Contribution by Cuisine",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Download ────────────────────────────────────────────────────────
    st.download_button(
        "📥 Download Current View",
        data=filtered.to_csv(index=False).encode(),
        file_name=f"Portfolio_{selected_month}_{selected_res.replace(' ','_')}.csv",
        mime="text/csv"
    )

else:
    st.info("Upload your CSV file to see the detailed portfolio dashboard")

st.caption("Interactive Portfolio Tracker • Attention flags + suggestions • Raja's Ajmer Restaurants")
