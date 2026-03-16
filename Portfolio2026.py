# ── Attention Needed Section ───────────────────────────────────────
st.subheader("🚨 Attention Needed – Restaurants Requiring Action")

# Make sure we know what "latest month" is
current_month = selected_month if selected_month != "All" else filtered['Month'].max()

attention = []
for _, row in filtered.iterrows():
    issues = []

    # Only flag zero orders if we're looking at the most recent data for that restaurant
    if row['Orders'] == 0:
        # Optional: only flag if this is the latest month for this restaurant
        res_latest = df[df['res_name'] == row['res_name']]['Month'].max()
        if row['Month'] == res_latest:
            issues.append("Zero orders in latest month")

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
        }).background_gradient(subset=['GMV'], cmap='OrRd_r'),
        use_container_width=True
    )

    st.markdown('<div class="attention-box"><strong>Quick Actions:</strong></div>', unsafe_allow_html=True)

    for _, r in att_df.iterrows():
        st.markdown(f"**{r['Restaurant']}** ({r['Month']}) – {r['Issues']}")
else:
    st.markdown('<div class="good-box"><strong>🟢 All good!</strong> No restaurants currently require urgent attention.</div>', unsafe_allow_html=True)
