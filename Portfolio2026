import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ajmer Restaurant Portfolio Tracker", layout="wide", page_icon="📊")
st.title("📊 Restaurant Portfolio MoM Dashboard – Ajmer")
st.markdown("**Upload your Res_level_txn CSV** (Jan + Feb + Mar 2026 or newer)")

uploaded = st.file_uploader("Choose CSV file", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()
    
    # Calculate key metrics
    df['Orders'] = df['delivered_ov'].fillna(0)
    df['CV'] = df['cv'].fillna(0)
    df['GMV'] = df['GMV'].fillna(0)
    df['Total_ov'] = df['Total_ov'].fillna(0)
    df['AOV'] = df.apply(lambda x: round(x['GMV']/x['Orders'], 1) if x['Orders'] > 0 else 0, axis=1)
    df['SL%'] = df.apply(lambda x: round(x['Orders']/x['Total_ov']*100, 1) if x['Total_ov'] > 0 else 0, axis=1)
    df['Month'] = df['Aggregation']
    
    # Portfolio summary
    summary = df.groupby('Month').agg({
        'Orders':'sum', 'CV':'sum', 'GMV':'sum', 'AOV':'mean', 'SL%':'mean'
    }).round(2)
    
    latest = df['Month'].max()
    cols = st.columns(5)
    cols[0].metric("Active Restaurants", len(df['res_name'].unique()))
    cols[1].metric("Total Orders", f"{int(summary.loc[latest,'Orders']):,}")
    cols[2].metric("Total GMV", f"₹{summary.loc[latest,'GMV']/1_00_000:.1f} Cr")
    cols[3].metric("Avg AOV", f"₹{summary.loc[latest,'AOV']:.0f}")
    cols[4].metric("Avg SL%", f"{summary.loc[latest,'SL%']:.1f}%")
    
    # MoM Table
    st.subheader("Restaurant-wise Month-on-Month")
    pivot = df.pivot_table(index=['res_name','res_cuisine_new'], 
                           columns='Month', 
                           values=['Orders','GMV','AOV','SL%'], 
                           aggfunc='sum').round(2)
    st.dataframe(pivot, use_container_width=True)
    
    # Top 10 Chart
    st.subheader(f"Top 10 Restaurants by GMV – {latest}")
    top10 = df[df['Month']==latest].groupby('res_name')['GMV'].sum().nlargest(10).reset_index()
    fig = px.bar(top10, x='GMV', y='res_name', orientation='h', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Single restaurant deep dive
    st.subheader("Deep Dive – Select Restaurant")
    res = st.selectbox("Restaurant", sorted(df['res_name'].unique()))
    res_df = df[df['res_name']==res].sort_values('Month')
    st.dataframe(res_df[['Month','Orders','CV','GMV','AOV','SL%']])
    
    # Download
    csv = pivot.to_csv().encode()
    st.download_button("📥 Download Full MoM Report", csv, "Portfolio_MoM_Report.csv", "text/csv")

else:
    st.info("👆 Upload your CSV file above to generate the live dashboard")
