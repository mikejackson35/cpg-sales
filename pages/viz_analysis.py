import streamlit as st
import pandas as pd
import plotly.express as px
import pygwalker as pyg
import streamlit.components.v1 as components

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
@st.cache_data
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

# st.markdown("<h1 style='text-align: center; color: orange;'>Visualize Data Here</h1>", unsafe_allow_html=True)
pyg_html = pyg.to_html(all_sales)

# pyg_html = pyg.walk(all_sales, dark='light', return_html=True)

components.html(pyg_html, height=1000, width=1500,scrolling=True)

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)