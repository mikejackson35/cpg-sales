import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import psycopg2
import secrets
import numpy as np


st.set_page_config(page_title='Charts',
                   page_icon=":bar_chart:",
                   layout='wide'
)

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

# ---- PULL IN DATA FROM POSTGRES DB ----
@st.cache_data
def get_connection():
    conn = st.connection('dot', type ="sql")
    all_sales = conn.query("SELECT * FROM level_2 WHERE date > '2021-12-31'")
    return all_sales

all_sales = get_connection()


# date cleanup
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

# --- FILTERS AND SIDEBAR ----

import datetime
today = datetime.datetime.now()
first_day = all_sales.date.min()

date_range = st.sidebar.date_input("Chose Dates",(first_day,today),first_day, today,format="MM.DD.YYYY")

start = date_range[0]
end = date_range[1]

segment = st.sidebar.multiselect(
    label='Market Segment',
    options=list(pd.Series(all_sales['market_segment'].unique())),
    default=list(pd.Series(all_sales['market_segment'].unique())),
)
sale_origin = st.sidebar.multiselect(
    label = 'Direct or Dot',
    options=np.array(all_sales['sale_origin'].unique()),
    default=np.array(all_sales['sale_origin'].unique()),
)

df_selection = all_sales[
    (all_sales['market_segment'].isin(segment)) &
    (all_sales['sale_origin'].isin(sale_origin))
    ]

# ---- TOP KPI's Row ----
df_selection['date'] = df_selection['date'].dt.date
sales_in_data = df_selection[(df_selection.date>start) & (df_selection.date<end)].usd.sum()

parent_count = int(df_selection[(df_selection.date>start) & (df_selection.date<end)].parent_customer.nunique())
customer_count = int(df_selection[(df_selection.date>start) & (df_selection.date<end)].customer.nunique())

st.markdown("")
blank, col0, col1, col2, col3 = st.columns([.12,.33,.33,.33,.33])
with blank:
    st.markdown(" ")
with col0:
    st.markdown("<h1 style='margin-left:10%;'>TRUE Sales</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-left:10%;'>Data Finder</h4>", unsafe_allow_html=True)
with col1:
    st.markdown("#")
    st.markdown('<h5>Showing</h5>', unsafe_allow_html=True)
    st.header(f"${sales_in_data:,.0f}")
with col2:
    st.markdown("#")
    st.markdown('<h5>Parent Customers</h5>', unsafe_allow_html=True)
    st.header(f"{parent_count}")
with col3:
    st.markdown("#")
    st.markdown('<h5>Child Customers</h5>', unsafe_allow_html=True)
    st.header(f"{customer_count}")

st.markdown("---")

## DOWNLOAD CSV BUTTON ###
@st.cache_data
def convert_df(df):
    return df_selection.to_csv().encode('utf-8')
csv = convert_df(df_selection)

blank, dl_button = st.columns([.1,.9])
blank.markdown("##")
dl_button.download_button(
    label="Download as CSV",
    data=csv,
    file_name='sales_download.csv',
    mime='text/csv',
)

blank, num_rows_text = st.columns([.1,.9])
blank.markdown("##")
num_rows_text.markdown(f"raw data  -  {len(df_selection)} rows")

table_to_display = df_selection[['date', 'sale_origin', 'market_segment', 'parent_customer', 'customer','item','qty','usd','cad','month','year']].sort_values(by='date',ascending=False).reset_index(drop=True)

table_to_display = table_to_display[(table_to_display.date>start) & (table_to_display.date<end)]

blank, table = st.columns([.1,.9])
blank.markdown("##")
table.dataframe(table_to_display.round(2), hide_index=True, height=800, use_container_width=True)

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)