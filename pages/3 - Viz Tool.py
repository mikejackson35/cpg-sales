import streamlit as st
import pandas as pd
import plotly.express as px
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer
import streamlit.components.v1 as components
# from sqlalchemy import create_engine
import psycopg2
import secrets
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

# TRUE
@st.cache_resource
def get_true():
    true_sales = pd.read_csv(r"true_ppg_sales.csv", encoding='utf-8')
    true_sales = true_sales[true_sales.status=='Closed']
    return StreamlitRenderer(true_sales)#, spec="./gw_config.json", spec_io_mode="rw")

renderer = get_true()
renderer.explorer()

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)