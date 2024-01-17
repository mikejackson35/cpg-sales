import streamlit as st
import pandas as pd
import plotly.express as px


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

st.markdown("<h1 style='margin-left:30%;'>Data Downloader</h1>", unsafe_allow_html=True)
st.markdown('##')
# ---- PULL IN DATA ----
# @st.cache_data
def get_data_from_csv():
    df = pd.read_csv('data/all_sales_data.csv')
    return df
df = get_data_from_csv()

### MASTER DATA ###
all_sales = df.copy()

# invoice date cleanup
all_sales['Invoice Date'] = pd.to_datetime(all_sales['Invoice Date'])
all_sales['Invoice Date'] = all_sales['Invoice Date'].dt.normalize()
all_sales['Invoice Date'] = all_sales['Invoice Date'].dt.floor('D')

# --- FILTERS AND SIDEBAR ----
# variables

year = st.sidebar.multiselect(
    "Year:",
    options=all_sales['Invoice Date'].dt.year.unique(),
    default=all_sales['Invoice Date'].dt.year.unique(),
)

segment = st.sidebar.multiselect(
    "Market Segment:",
    options=all_sales['Market Segment'].unique(),
    default=all_sales['Market Segment'].unique(),
)

# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = all_sales[
    (all_sales['Invoice Date'].dt.year.isin(year)) &
    (all_sales['Market Segment'].isin(segment))
    ]

# ---- TOP KPI's Row ----
sales_in_data = df_selection.Dollars.sum()
sales_23 = int(all_sales[all_sales["Invoice Date"].dt.year == 2023].Dollars.sum())
sales_22 = all_sales[all_sales['Invoice Date'].dt.year == 2022]['Dollars'].sum().round(2)
# delta = sales_23 - sales_22

def plus_minus(delta):
    if delta > 0:
        symbol = "+"
    else:
        symbol = ""
    return symbol

delta = sales_23 - sales_22
yoy_chg_perc = plus_minus(delta) + f"{int(sales_23/sales_22*100-100)}%"
mean_sales = int(all_sales[all_sales["Invoice Date"].dt.year == 2023].Dollars.mean())
parent_count = int(df_selection['Parent Customer'].nunique())
customer_count = int(df_selection.Customer.nunique())

# blank, col1, col2, col3, col4 = st.columns([.33,1.1,1,1,.5])
blank, col1, col2, col3 = st.columns([.12,.33,.33,.33])
with blank:
    st.markdown(" ")
with col1:
    st.markdown('<h4>Total Sales in Data</h4>', unsafe_allow_html=True)
    st.title(f"${sales_in_data:,.0f}")
with col2:
    st.markdown('<h4>Parent Customers</h4>', unsafe_allow_html=True)
    st.title(f"{parent_count}")
with col3:
    st.markdown('<h4>Child Customers</h4>', unsafe_allow_html=True)
    st.title(F"{customer_count:,}")
# with col3:
#     st.markdown(" ")

# line divider
st.markdown("---")

## DOWNLOAD CSV BUTTON ###
# @st.cache_data
def convert_df(df):
    # preventing computation on every rerun
    return df_selection.to_csv().encode('utf-8')

csv = convert_df(df_selection)

blank, dl_button = st.columns([.1,.9])
blank.markdown("##")
dl_button.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='sales_download.csv',
    mime='text/csv',
)

blank, num_rows_text = st.columns([.1,.9])
blank.markdown("##")
num_rows_text.markdown(f"raw data  -  {len(df_selection)} rows")

table_to_display = df_selection[['Invoice Date', 'Sale Origin', 'Market Segment', 'Parent Customer', 'Customer', 'Customer Order Number','Item Full Description','Dollars']].sort_values(by='Invoice Date').reset_index(drop=True)

blank, table = st.columns([.1,.9])
blank.markdown("##")
table.dataframe(table_to_display.round(2))

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)