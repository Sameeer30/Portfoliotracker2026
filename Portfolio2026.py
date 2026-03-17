import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ───────────────────────────────────────────────
# Page configuration
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="JF25 vs JF26 Restaurant Dashboard",
    page_icon="🍽️📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ───────────────────────────────────────────────
# Title & header
# ───────────────────────────────────────────────
st.title("🍽️ Restaurant Performance Dashboard — JF25 vs JF26")
st.markdown("**Comparison of orders, growth, portfolio & city-wise contribution** — Jaipur area restaurants")

# ───────────────────────────────────────────────
# Hard-coded data (your table pasted & lightly cleaned)
# ───────────────────────────────────────────────
@st.cache_data
def get_data():
    data = {
        "Res Id": [18691988, 20775459, 20529922, 19596889, 22168043, 22336162, 22168177, 21261889, 19648663, 19484087],
        "Res Name": [
            "Roti Boti", "Royal Chinese", "Masala Nama", "The Momo Story", "Surbhi Sweets - Signature Food",
            "Mittal’s - Guaranteed Delivery", "Bikaner Misthan Bhandar", "Night Owl World", "Habibi Cafe", "S.B Fast Food"
        ],
        "Cuisine": [
            "North Indian", "Chinese", "North Indian", "Street Food", "North Indian",
            "North Indian", "Mithai", "Pizza", "Chinese", "Fast Food"
        ],
        "JF25_Orders": [1329, 643, 787, 390, 0, 0, 0, 95, 333, 284],
        "JF26_Orders": [1716, 994, 617, 580, 780, 720, 543, 493, 485, 771],
        "Growth_pct": [0.2912, 0.5459, -0.2160, 0.4872, 0.0, 0.0, 0.0, 0.1895, 0.4565, 1.60357],
        "Port_Cont_25": [0.2912, 0.0459, 0.0038, 0.0019, 0.0, 0.0, 0.0, 0.0005, 0.0016, 0.0001],
        "Port_Cont_26": [0.0064, 0.0031, 0.0019, 0.0016, 0.0048, 0.0048, 0.0045, 0.00147, 0.00133, 0.00146],
        "Port_Delta": [0.0529, 0.0306, -0.0029, 0.0009, 0.0048, 0.0048, 0.0045, 0.0031, 0.0006, 0.0037],
        "City_Cont_25": [0.0465, 0.0275, 0.0081, 0.0040, 0.0, 0.0, 0.0, 0.0010, 0.0034, 0.0003],
        "City_Cont_26": [0.0136, 0.0066, 0.0052, 0.0048, 0.0048, 0.0048, 0.0045, 0.0041, 0.0041, 0.0040],
        "City_Delta": [0.0007, 0.0017, -0.0029, 0.0009, 0.0048, 0.0048, 0.0045, 0.0031, 0.0006, 0.0037]
    }

    df = pd.DataFrame(data)

    # Calculate derived columns
    df["Total_Orders"] = df["JF25_Orders"] + df["JF26_Orders"]
    df["Abs_Growth"] = df["JF26_Orders"] - df["JF25_Orders"]

    # For better display
    df["Growth_%"] = (df["Growth_pct"] * 100).round(1).astype(str) + "%"
    df["Port_Cont_26_%"] = (df["Port_Cont_26"] * 100).round(2).astype(str) + "%"
    df["City_Cont_26_%"] = (df["City_Cont_26"] * 100).round(2).astype(str) + "%"

    return df.sort_values("JF26_Orders", ascending=False).reset_index(drop=True)


df = get_data()

# ───────────────────────────────────────────────
# Sidebar – filters
# ───────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    selected_cuisines = st.multiselect(
        "Cuisine",
        options=sorted(df["Cuisine"].unique()),
        default=sorted(df["Cuisine"].unique())
    )

    min_orders = st.slider(
        "Minimum JF26 Orders",
        0, int(df["JF26_Orders"].max()),
        0
    )

    show_top_n = st.slider("Show top N restaurants", 5, 30, 15)

df_f = df[
    (df["Cuisine"].isin(selected_cuisines)) &
    (df["JF26_Orders"] >= min_orders)
].head(show_top_n)

# ───────────────────────────────────────────────
# KPI cards
# ───────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.4])

with col1:
    st.metric("Total JF26 Orders", f"{df_f['JF26_Orders'].sum():,}")

with col2:
    st.metric("Total JF25 Orders", f"{df_f['JF25_Orders'].sum():,}")

with col3:
    growth = (df_f["JF26_Orders"].sum() - df_f["JF25_Orders"].sum()) / df_f["JF25_Orders"].sum()
    st.metric("Overall Growth", f"{growth:+.1%}")

with col4:
    st.metric("Restaurants shown", len(df_f))

with col5:
    top_rest = df_f.iloc[0]["Res Name"]
    top_orders = df_f.iloc[0]["JF26_Orders"]
    st.metric("Top performer", f"{top_rest}\n({top_orders:,} orders)")

# ───────────────────────────────────────────────
# Tabs
# ───────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Orders", "🏆 Ranking", "📈 Contribution", "🗃️ Raw Data"])

with tab1:
    st.subheader("JF25 vs JF26 Orders — Top restaurants")

    melted = df_f.melt(
        id_vars=["Res Name", "Cuisine"],
        value_vars=["JF25_Orders", "JF26_Orders"],
        var_name="Period", value_name="Orders"
    )
    melted["Period"] = melted["Period"].replace({"JF25_Orders": "JF25", "JF26_Orders": "JF26"})

    fig_orders = px.bar(
        melted,
        x="Res Name",
        y="Orders",
        color="Period",
        barmode="group",
        title="Orders comparison — filtered restaurants",
        height=520,
        color_discrete_sequence=["#636EFA", "#EF553B"]
    )
    fig_orders.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_orders, use_container_width=True)

with tab2:
    st.subheader("Ranking — JF26 Orders")

    fig_rank = px.bar(
        df_f.head(show_top_n),
        x="Res Name",
        y="JF26_Orders",
        color="Growth_pct",
        hover_data=["Growth_%", "Cuisine", "JF25_Orders"],
        title="Top restaurants by JF26 orders (color = growth %)",
        height=540
    )
    fig_rank.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_rank, use_container_width=True)

with tab3:
    st.subheader("Portfolio & City Contribution — JF26")

    fig_scatter = px.scatter(
        df_f,
        x="Port_Cont_26",
        y="City_Cont_26",
        size="JF26_Orders",
        color="Cuisine",
        hover_name="Res Name",
        hover_data=["Growth_%", "JF26_Orders"],
        title="Portfolio vs City contribution — bubble size = JF26 orders",
        height=520
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.subheader("Filtered raw data")
    st.dataframe(
        df_f[[
            "Res Name", "Cuisine",
            "JF25_Orders", "JF26_Orders", "Growth_%",
            "Port_Cont_26_%", "City_Cont_26_%"
        ]],
        use_container_width=True,
        hide_index=False
    )

# ───────────────────────────────────────────────
# Footer
# ───────────────────────────────────────────────
st.markdown("---")
st.caption("Data sample limited to top rows • Growth and contribution values approximated from input • Created with Streamlit + Plotly • March 2026")
