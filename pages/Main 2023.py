import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sqlalchemy import create_engine
import psycopg2
import secrets
import numpy as np


st.set_page_config(page_title='Main Page',
                   page_icon=":bar_chart:",
                   layout='wide'
)

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #E09641;
    color: #5A5856;
    text-align: center;
    padding: 15px 0;
    
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 900;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
    # font-weight: 900;
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
    # font-weight: 900;
}

</style>
""", unsafe_allow_html=True)

# ---- PULL IN DATA FROM POSTGRES DB ----
@st.cache_data
def get_connection():
    conn = st.connection('dot', type ="sql")
    all_sales = conn.query("SELECT * FROM level_2 WHERE date > '2021-12-31' AND date < '2024-01-01'")
    return all_sales

all_sales = get_connection()

# invoice date cleanup
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

st.sidebar.image(r"assets/Nevil.png")

st.markdown("<h1 style='text-align: center;'>2023 AWAKE</h1>", unsafe_allow_html=True)
st.markdown("##")

# ---- TOP KPI's Row ----
sales_23 = int(all_sales[all_sales['date'].dt.year == 2023].usd.sum())
sales_22 = all_sales[all_sales['date'].dt.year == 2022]['usd'].sum().round(2)

def plus_minus(delta):
    if delta > 0:
        symbol = "+"
    else:
        symbol = ""
    return symbol

delta = sales_23 - sales_22
yoy_chg_perc = plus_minus(delta) + f"{int(sales_23/sales_22*100-100)}%"
customer_count = int(all_sales[all_sales['date'].dt.year == 2023].customer.nunique())
sales = all_sales[all_sales['date'].dt.year == 2023]['usd'].sum()
mean_sales = int(sales/customer_count)

logo, col1, col2, col3, col4 = st.columns([.5,1.13,1.13,1.13,1.12])
with logo:
    st.markdown(" ")
with col1:
    st.markdown('<h4>Sales</h4>', unsafe_allow_html=True)
    st.title(f"${sales_23:,}")
with col2:
    st.markdown('<h4>vs. 2022</h4>', unsafe_allow_html=True)
    st.title(f"{yoy_chg_perc}")
with col3:
    st.markdown('<h4>Num of Customers</h4>', unsafe_allow_html=True)
    st.title(F"{customer_count:,}")
with col4:
    st.markdown('<h4>$/Customer</h4>', unsafe_allow_html=True)
    st.title(f"${mean_sales:,}")

# line divider
st.markdown("---")


st.markdown("<b><h2 style='text-align: center;'>Market Segments</h2></b>", unsafe_allow_html=True)

all_sales['date'] = pd.to_datetime(all_sales['date'])

# METRICS
vending_23 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Vending')].usd.sum()
vending_22 = all_sales[(all_sales['date'].dt.year == 2022) & (all_sales['market_segment'] == 'Vending')].usd.sum()
yoy_vend = int(vending_23-vending_22)
yoy_vend_perc = round(int(vending_23-vending_22) / vending_22,2)


# online = all_sales[(all_sales.market_segment == 'Online Direct') | (all_sales.market_segment=='Online Distributor')]
online_23 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Online')].usd.sum()
online_22 = all_sales[(all_sales['date'].dt.year == 2022) & (all_sales['market_segment'] == 'Online')].usd.sum()
yoy_online = int(online_23-online_22)
yoy_online_perc = round(int(online_23-online_22) / online_22,2)

alt_23 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Alternate Retail')].usd.sum()
alt_22 = all_sales[(all_sales['date'].dt.year == 2022) & (all_sales['market_segment'] == 'Alternate Retail')].usd.sum()
yoy_alt = int(alt_23-alt_22)
yoy_alt_perc = round(int(alt_23-alt_22) / alt_22,2)

conv_23 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Convenience')].usd.sum()
conv_22 = all_sales[(all_sales['date'].dt.year == 2022) & (all_sales['market_segment'] == 'Convenience')].usd.sum()
yoy_conv = int(conv_23-conv_22)
yoy_conv_perc = round(int(conv_23-conv_22) / conv_22,2)

canada_23 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Canada')].usd.sum()
canada_22 = all_sales[(all_sales['date'].dt.year == 2022) & (all_sales['market_segment'] == 'Canada')].usd.sum()
yoy_canada = int(canada_23-canada_22)
yoy_canada_perc = round(int(canada_23-canada_22) / canada_22,2)

grocery_23 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Grocery')].usd.sum()
grocery_22 = all_sales[(all_sales['date'].dt.year == 2022) & (all_sales['market_segment'] == 'Grocery')].usd.sum()
yoy_grocery = int(grocery_23-grocery_22)
yoy_grocery_perc = round(int(grocery_23-grocery_22) / grocery_22,2)

# next line of metrics
broadline_23 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Broadline Distributor')].usd.sum()
broadline_22 = all_sales[(all_sales['date'].dt.year == 2022) & (all_sales['market_segment'] == 'Broadline Distributor')].usd.sum()
yoy_broadline = int(broadline_23-broadline_22)
yoy_broadline_perc = round(int(broadline_23-broadline_22) / broadline_22,2)


other_23 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Other')].usd.sum()
other_22 = all_sales[(all_sales['date'].dt.year == 2022) & (all_sales['market_segment'] == 'Other')].usd.sum()
yoy_other = int(other_23-other_22)
yoy_other_perc = round(int(other_23-other_22) / other_22,2)

# BEGIN ROWS AND COLUMNS METRICS
blank,col1, col2, col3, col4, blank = st.columns([1,2,2,2,2,1])

blank.markdown("")
col1.metric(label='Vending', value=f"${int(vending_23):,}", delta = f"{yoy_vend_perc:.0%}")
col2.metric(label='Online', value=f"${int(online_23):,}", delta = f"{yoy_online_perc:.0%}")
col3.metric(label='Alternate Retail', value=f"${int(alt_23):,}", delta = f"{yoy_alt_perc:.0%}")
col4.metric(label='Canada', value=f"${int(canada_23):,}", delta = f"{yoy_canada_perc:.0%}")
blank.markdown("")

st.markdown("##")
st.markdown("##")

blank,col1, col2, col3, col4, blank = st.columns([1,2,2,2,2,1])

blank.markdown("")
col1.metric(label='Convenience', value=f"${int(conv_23):,}", delta = f"{yoy_conv_perc:.0%}")
col2.metric(label='Grocery', value=f"${int(grocery_23):,}", delta = f"{yoy_grocery_perc:.0%}")
col3.metric(label='Broadline', value=f"${int(broadline_23):,}", delta = f"{yoy_broadline_perc:.0%}")
col4.metric(label='Other', value=f"${int(other_23):,}", delta = f"{yoy_other_perc:.0%}")
blank.markdown("")




# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)