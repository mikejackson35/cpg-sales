import streamlit as st
import pandas as pd
import plotly.express as px
import pygwalker as pyg
import streamlit.components.v1 as components
from sqlalchemy import create_engine
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

# ---- PULL IN DATA FROM POSTGRES DB ----
conn = st.connection('dot', type ="sql")
all_sales = conn.query("SELECT * FROM level_2 WHERE date > '2020-12-31'")

# date cleanup
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')
pyg_html = pyg.to_html(all_sales)

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