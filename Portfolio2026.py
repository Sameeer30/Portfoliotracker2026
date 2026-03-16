import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Ajmer Restaurant Portfolio Tracker", layout="wide", page_icon="📊")
st.title("📊 Restaurant Portfolio MoM Dashboard – Ajmer")
st.markdown("Upload your Res_level_txn CSV (supports Jan–Mar 2026 and newer)")

# ────────────────────────────────────────────────
# File upload & basic cleaning
# ────────────────────────────────────────────────
uploaded = st.file_uploader("Choose CSV file", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()

    # Core metrics
    df['Month']       = df['Aggregation']
    df['Orders']      = df['delivered_ov'].fillna(0).astype(float)
    df['CV']          = df['cv'].fillna(0).astype(float)
    df['GMV']         = df['GMV'].fillna(0).astype(float)
    df['Total_ov']    = df['Total_ov'].fillna(0).astype(float)
    df['AOV']         = df.apply(lambda x: round(x['GMV']/x['Orders'],1) if x['Orders']>0 else 0, axis=1)
    df['SL_pct']      = df.apply(lambda x: round(x['Orders']/x['Total_ov']*100,1) if x['Total_ov']>0 else 0, axis=1)

    # ── Ads related columns ───────────────────────────────
    df['Ads_Booked']  = df['booked_amount'].fillna(0).astype(float)
    df['Ads_Billed']  = df['billed_amount'].fillna(0).astype(float)
    df['Ads_CV']      = df['ads_cv'].fillna(0).astype(float)
    df['Ads_GMV']     = df['ads_gmv'].fillna(0).astype(float)
    df['Ads_CV_pct']  = df.apply(lambda x: round(x['Ads_CV']/x['CV']*100,1) if x['CV']>0 else 0, axis=1)

    # Sort months chronologically
    df = df.sort_values(['res_name', 'Month'])

    # ────────────────────────────────────────────────
    # Portfolio KPIs
    # ────────────────────────────────────────────────
    latest_month = df['Month'].max()
    prev_month   = sorted(df['Month'].unique())[-2] if len(df['Month'].unique()) >= 2 else None

    portfolio = df[df['Month'] == latest_month].agg({
        'Orders': 'sum',
        'GMV': 'sum',
        'CV': 'sum',
        'AOV': 'mean',
        'SL_pct': 'mean',
        'Ads_Booked': 'sum',
        'Ads_Billed': 'sum',
        'Ads_CV_pct': 'mean'
    }).round(2)

    if prev_month:
        prev_port = df[df['Month'] == prev_month].agg({
            'Orders': 'sum', 'GMV': 'sum'
        }).round(2)
        orders_mom = (portfolio['Orders'] - prev_port['Orders']) / prev_port['Orders'] * 100 if prev_port['Orders'] > 0 else 0
        gmv_mom    = (portfolio['GMV']    - prev_port['GMV'])    / prev_port['GMV']    * 100 if prev_port['GMV']    > 0 else 0
    else:
        orders_mom = gmv_mom = None

    cols = st.columns(5)
    cols[0].metric("Active Restaurants", len(df[df['Month']==latest_month]['res_name'].unique()))
    cols[1].metric("Orders (latest)", f"{int(portfolio['Orders']):,}", f"{orders_mom:+.1f}%" if orders_mom is not None else "—")
    cols[2].metric("GMV (latest)",    f"₹{portfolio['GMV']/1e5:,.1f} L", f"{gmv_mom:+.1f}%" if gmv_mom is not None else "—")
    cols[3].metric("Avg AOV",         f"₹{portfolio['AOV']:,.0f}")
    cols[4].metric("Avg Ads/CV %",    f"{portfolio['Ads_CV_pct']:.1f}%")

    # ────────────────────────────────────────────────
    # Charts – Row 1
    # ────────────────────────────────────────────────
    st.subheader(f"Visual Overview – {latest_month}")

    c1, c2 = st.columns(2)

    with c1:
        top10 = df[df['Month']==latest_month].nlargest(10, 'GMV')[['res_name','GMV','Orders','AOV']]
        fig_bar = px.bar(top10, x='GMV', y='res_name', orientation='h',
                         text_auto=True, title="Top 10 by GMV",
                         color='GMV', color_continuous_scale='bluered')
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        trend = df.groupby('Month')[['Orders','GMV']].sum().reset_index()
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=trend['Month'], y=trend['Orders'], name="Orders", yaxis="y"))
        fig_line.add_trace(go.Scatter(x=trend['Month'], y=trend['GMV']/1e5,   name="GMV (Lakh)", yaxis="y2"))
        fig_line.update_layout(
            title="Portfolio Trend",
            yaxis=dict(title="Orders"),
            yaxis2=dict(title="GMV (₹ Lakh)", overlaying="y", side="right")
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # ────────────────────────────────────────────────
    # Restaurant selector + detailed view
    # ────────────────────────────────────────────────
    st.subheader("Restaurant Deep Dive")

    res_list = sorted(df['res_name'].unique())
    selected_res = st.selectbox("Select Restaurant", res_list, index=0)

    if selected_res:
        res_df = df[df['res_name'] == selected_res].sort_values('Month')

        # Flags logic
        if len(res_df) >= 2:
            last = res_df.iloc[-1]
            prev = res_df.iloc[-2]
            gmv_change = (last['GMV'] - prev['GMV']) / prev['GMV'] * 100 if prev['GMV'] > 0 else 0
            ord_change = (last['Orders'] - prev['Orders']) / prev['Orders'] * 100 if prev['Orders'] > 0 else 0

            if last['Orders'] == 0 and prev['Orders'] > 20:
                flag = "🔴 CRITICAL – Dropped to zero orders"
                flag_color = "red"
            elif gmv_change <= -30 or ord_change <= -30:
                flag = f"🔴 Strong drop ({gmv_change:+.1f}% GMV / {ord_change:+.1f}% Orders)"
                flag_color = "red"
            elif gmv_change >= 30 or ord_change >= 30:
                flag = f"🟢 Strong growth ({gmv_change:+.1f}% GMV / {ord_change:+.1f}% Orders)"
                flag_color = "green"
            else:
                flag = "→ Stable / minor change"
                flag_color = "gray"
        else:
            flag = "→ New or single-month restaurant"
            flag_color = "blue"

        st.markdown(f"**Status Flag:** <span style='color:{flag_color}; font-weight:bold; font-size:1.2em;'>{flag}</span>", unsafe_allow_html=True)

        # Detailed table
        cols_show = ['Month','Orders','CV','GMV','AOV','SL_pct','Ads_Booked','Ads_Billed','Ads_CV_pct','Ads_GMV']
        st.dataframe(res_df[cols_show].style.format({
            'GMV':'₹{:,.0f}',
            'CV':'₹{:,.0f}',
            'Ads_Booked':'₹{:,.0f}',
            'Ads_Billed':'₹{:,.0f}',
            'Ads_GMV':'₹{:,.0f}',
            'AOV':'₹{:.1f}',
            'SL_pct':'{:.1f}%',
            'Ads_CV_pct':'{:.1f}%'
        }), use_container_width=True)

        # Mini chart for selected restaurant
        fig_res = px.line(res_df, x='Month', y=['Orders','GMV'], 
                          title=f"{selected_res} – Orders & GMV Trend",
                          markers=True)
        st.plotly_chart(fig_res, use_container_width=True)

    # ────────────────────────────────────────────────
    # Download full cleaned + pivoted data
    # ────────────────────────────────────────────────
    pivot = df.pivot_table(
        index=['res_name','res_cuisine_new'],
        columns='Month',
        values=['Orders','GMV','AOV','SL_pct','Ads_Booked','Ads_CV_pct'],
        aggfunc='first'
    ).round(2)

    csv = pivot.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Download Full MoM Report (csv)",
        data=csv,
        file_name=f"portfolio_mom_{latest_month}.csv",
        mime="text/csv"
    )

else:
    st.info("Upload your CSV file above to see the dashboard")

st.markdown("---")
st.caption("Features: Ads metrics • MoM flags (red/green) • Portfolio & restaurant charts • Downloadable report")
