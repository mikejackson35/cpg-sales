import streamlit as st
import pandas as pd
import plotly.express as px
import pygwalker as pyg
import streamlit.components.v1 as components
# from sqlalchemy import create_engine
# import secrets
import numpy as np

st.set_page_config(page_title='Main Page',
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

# ---- PULL IN DATA ----
## ----- CONNECT TO POSTGRESQL DATABASE --------
# connection_string = f"postgresql://{st.secrets['db_user']}:{st.secrets['db_password']}@{st.secrets['endpoint']}:5432/{st.secrets['db_name']}"
# engine = create_engine(connection_string)

# ---- PULL IN DATA ----
@st.cache_data
def get_data_from_csv():
    # df = pd.read_sql("SELECT * FROM level_2 WHERE year > '2020'",con = engine)
    df = pd.read_csv(r"data/all_sales_data.csv")
    return df
df = get_data_from_csv()

all_sales = df.copy()

# date cleanup
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

# st.markdown("<h1 style='text-align: center; color: orange;'>Visualize Data Here</h1>", unsafe_allow_html=True)
pyg_html = pyg.to_html(all_sales)

# pyg_html = pyg.walk(all_sales, dark='light', return_html=True)

components.html(pyg_html, height=1000, width=1700,scrolling=True)

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)