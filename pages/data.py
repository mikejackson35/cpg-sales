import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine


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


## ----- CONNECT TO POSTGRESQL DATABASE --------

db_password = "UnitCircle42!"
db_user = "postgres"
db_name = "dot"
endpoint = "awakedb.cre3f7yk1unp.us-west-1.rds.amazonaws.com"

connection_string = f"postgresql://{db_user}:{db_password}@{endpoint}:5432/{db_name}"
engine = create_engine(connection_string)


# ---- PULL IN DATA ----
@st.cache_data
def get_data_from_csv():
    df = pd.read_csv(r"data/all_sales_data.csv")
@st.cache_data
def get_data_from_csv():
    df = pd.read_sql("""
            SELECT * 
            FROM level_2
            WHERE year > '2020'
            """
            ,con = engine)
    return df
df = get_data_from_csv()

### MASTER DATA ###
all_sales = df.copy()
# all_sales = all_sales.convert_dtypes()


st.markdown("<h1 style='margin-left:30%;'>Data Downloader</h1>", unsafe_allow_html=True)
st.markdown('##')


# date cleanup
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

# --- FILTERS AND SIDEBAR ----

year = st.sidebar.multiselect(
    label = 'Year',
    options=sorted(list(all_sales['year'].unique())),
    default=sorted(list(all_sales['year'].unique()))
)

segment = st.sidebar.multiselect(
    label='Market Segment',
    options=list(pd.Series(all_sales['market_segment'].unique())),
    default=list(pd.Series(all_sales['market_segment'].unique())),
)

# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = all_sales[
    (all_sales['date'].dt.year.isin(year)) &
    (all_sales['market_segment'].isin(segment))
    ]

# ---- TOP KPI's Row ----
sales_in_data = df_selection.usd.sum()

def plus_minus(delta):
    if delta > 0:
        symbol = "+"
    else:
        symbol = ""
    return symbol

parent_count = int(df_selection.parent_customer.nunique())
customer_count = int(df_selection.customer.nunique())

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

table_to_display = df_selection[['date', 'sale_origin', 'market_segment', 'parent_customer', 'customer','item','qty','usd','cad','month','year']].sort_values(by='date',ascending=False).reset_index(drop=True)
table_to_display['date'] = table_to_display['date'].dt.date
table_to_display['year'] = table_to_display['year'].astype('category')

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