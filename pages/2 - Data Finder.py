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
# GET DATA
###############

# TRUE
@st.cache_data
def get_true():
    true_sales = pd.read_csv(r"C:\Users\mikej\Desktop\cpg-sales\data\true_sales.csv", encoding='utf-8')
    true_sales = true_sales[true_sales.status=='Closed']
    return true_sales
true_sales = get_true()


# date cleanup
true_sales['date'] = pd.to_datetime(true_sales['date'])
true_sales['date'] = true_sales['date'].dt.normalize()
true_sales['date'] = true_sales['date'].dt.floor('D')

# --- FILTERS AND SIDEBAR ----

import datetime
today = datetime.datetime.now()
this_year = today.year
jan_1 = datetime.date(this_year, 1, 1)


date_range = st.sidebar.date_input("Chose Dates",(jan_1,today),jan_1, today,format="MM.DD.YYYY")

start = date_range[0]
end = date_range[1]

source = st.sidebar.multiselect(
    label = 'Direct or Dot',
    options=np.array(true_sales['source'].unique()),
    default=np.array(true_sales['source'].unique()),
)

segment = st.sidebar.multiselect(
    label='Market Segment',
    options=list(pd.Series(true_sales['cust_segment'].unique())),
    default=list(pd.Series(true_sales['cust_segment'].unique())),
)

parent_customer = st.sidebar.multiselect(
    label='Parent Customer',
    options=list(pd.Series(true_sales['cust_parent_name'].unique())),
    default=list(pd.Series(true_sales['cust_parent_name'].unique())),
)

df_selection = true_sales[
    (true_sales['cust_segment'].isin(segment)) &
    (true_sales['source'].isin(source))
    ]

# ---- TOP KPI's Row ----
df_selection['date'] = df_selection['date'].dt.date
sales_in_data = df_selection[(df_selection.date>start) & (df_selection.date<end)].amount.sum()

parent_count = int(df_selection[(df_selection.date>start) & (df_selection.date<end)].cust_parent_name.nunique())
customer_count = int(df_selection[(df_selection.date>start) & (df_selection.date<end)].cust_name.nunique())

st.markdown("")
blank, col0, col1, col2, col3 = st.columns([.12,.33,.33,.33,.33])
with blank:
    st.markdown(" ")
with col0:
    st.markdown("<h1 style='margin-left:10%;'>True Sales</h1>", unsafe_allow_html=True)
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
    return df_selection.to_csv(index=False).encode('utf-8')
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

table_to_display = df_selection[['date', 'source', 'cust_segment', 'cust_parent_name', 'cust_name','amount']].sort_values(by='date',ascending=False).reset_index(drop=True)

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