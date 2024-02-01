import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sqlalchemy import create_engine
import psycopg2
import secrets
import numpy as np
from datetime import datetime


st.set_page_config(page_title='Awake YTD',
                   page_icon='assets/Nevil.png',
                   layout='wide'
)

alt.themes.enable("dark")

#######################
# CSS styling for metrics
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
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

# ---- PULL IN DATA FROM POSTGRES DB ----
@st.cache_data
def get_connection():
    conn = st.connection('dot', type ="sql")
    all_sales = conn.query("SELECT * FROM level_2 WHERE date > '2022-12-31'")
    return all_sales

all_sales = get_connection()

# date cleanup
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

market_segment_color = {
    'Vending': 'rgb(56,149,73)',
    'Grocery': 'rgb(248,184,230)',
    'Alternate Retail': 'rgb(46,70,166)',
    'Canada': 'rgb(204,208,221)',
    'Online': 'rgb(106,87,63)',
    'Other': 'rgb(200,237,233)',
    'Convenience': 'rgb(233,81,46)',
    'Broadline Distributor': 'rgb(233,152,19)',
    'Samples': 'rgb(141,62,92)'}

# LOGO AND TITLE
st.sidebar.image(r"assets/Nevil.png", width=200)
# st.markdown("<h1 style='text-align: center;'>2024 YTD</h1>", unsafe_allow_html=True)
# st.markdown("##")

col1, blank, col2 = st.columns([3.5,.5,1])

with col2:
######################
    def make_daily_bar_df(df):
        return (
            df.dropna()
            .assign(new_date=pd.to_datetime(all_sales['date']))
            .drop(columns=['cad','month','year','date'])
            .rename(columns={'new_date':'date'})
            .groupby(['market_segment','date'],as_index=False)
            .sum()
            .set_index('date')
            .sort_index()
        )

    daily_bar_df = make_daily_bar_df(all_sales)

    week_ago = datetime.today().date() - pd.offsets.Day(11)
    daily_bar_df = daily_bar_df[daily_bar_df.index > week_ago].sort_index()

    config = {'displayModeBar': False}

    fig = px.scatter(round(daily_bar_df),
            x='usd',
            color='market_segment',
            color_discrete_map=market_segment_color,
            labels={'date':"", 'usd':''},
            hover_name=daily_bar_df.index.date,
            height=700,
            width=275,
            opacity=.8,
            template='presentation',
            size='usd',
            size_max=25
            )#.update_traces(marker_size=20)
    
    fig.update_xaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=16))
    fig.update_yaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=14))
    fig.update_layout(xaxis={'side':'top'})

    fig.update_traces(marker=dict(line=dict(width=1,color='grey')),selector=dict(mode='markers'))
    fig.update_layout(showlegend=False)

    def make_daily_bar_dfb(df):
        return (
            df.dropna()
            .assign(new_date=pd.to_datetime(all_sales['date']))
            .drop(columns=['cad','month','year','date'])
            .rename(columns={'new_date':'date'})
            .groupby(['sale_origin','date'],as_index=False)
            .sum()
            .set_index('date')
            .sort_index()
        )

    daily_bar_dfb = make_daily_bar_dfb(all_sales)

    week_ago = datetime.today().date() - pd.offsets.Day(11)
    daily_bar_dfb = daily_bar_dfb[daily_bar_dfb.index > week_ago].sort_index()

    figb = px.scatter(round(daily_bar_dfb),
        x='usd',
        color='sale_origin',
        color_discrete_map={'unl':"#E62F29",'dot':"#3A4DA1"},
        labels={'date':"", 'usd':''},
        hover_name=daily_bar_dfb.index.date,
        height=700,
        width=275,
        opacity=.8,
        template='presentation',
        size='usd',
        size_max=25
        )#.update_traces(marker_size=20)
    
    figb.update_xaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=16))
    figb.update_yaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=14))
    figb.update_layout(xaxis={'side':'top'})

    figb.update_traces(marker=dict(line=dict(width=1,color='grey')),selector=dict(mode='markers'))
    figb.update_layout(showlegend=False)

   
   
    st.markdown("####")

    cola,colb = st.columns([.8,2])
    with cola:
        st.markdown("")
    with colb:
        st.write("**Sales Last 10 Days**",unsafe_allow_html=True)
    daily_choice = st.radio("Color Chart by...",
                ['Market Segment','Dot/Direct'],
                index=None)
    if daily_choice == 'Market Segment':
        st.plotly_chart(fig,config=config)
    else:
        st.plotly_chart(figb,config=config)
        

with col1:
    st.markdown("<h1 style='text-align: center;'>2024 YTD</h1>", unsafe_allow_html=True)
    st.markdown("##")
    # CALCS FOR KPI'S
    current_date = datetime.today().strftime('%Y-%m-%d')
    import datetime
    year_ago_today = datetime.datetime.today() - datetime.timedelta(days=365)

    sales_24 = int(all_sales[(all_sales['date'] > '2023-12-31') & (all_sales['date'] < current_date)].usd.sum())
    sales_23 = int(all_sales[(all_sales['date'] > '2022-12-31') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum())

    yoy_chg_perc = f"{int(sales_24/sales_23*100-100)}%"
    customer_count = int(all_sales[all_sales['date'].dt.year == 2024].customer.nunique())
    mean_sales = int(sales_24/customer_count)

    # TOP KPI'S
    logo, col1, col2, col3, col4 = st.columns([.5,1.13,1.13,1.13,1.12])
    with logo:
        st.markdown(" ")
    with col1:
        st.markdown('<h4>Sales</h4>', unsafe_allow_html=True)
        st.title(f"${sales_24:,}")
    with col2:
        st.markdown('<h4>YoY Change</h4>', unsafe_allow_html=True)
        st.title(f"{yoy_chg_perc}")
    with col3:
        st.markdown('<h4>Num of Customers</h4>', unsafe_allow_html=True)
        st.title(F"{customer_count:,}")
    with col4:
        st.markdown('<h4>$/Customer</h4>', unsafe_allow_html=True)
        st.title(f"${mean_sales:,}")

    # line divider & sub-title
    st.markdown("---")
    st.markdown("<b><h2 style='text-align: center;'>Market Segments</h2></b>", unsafe_allow_html=True)

    ###################

    all_sales['date'] = pd.to_datetime(all_sales['date'])

    # METRICS CALCS FOR THE 8 MARKET SEGMENTS
    vending_23 = all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == 'Vending')].usd.sum()
    vending_22 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Vending') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum()
    yoy_vend = int(vending_23-vending_22)
    yoy_vend_perc = round(int(vending_23-vending_22) / vending_22,2)

    online_23 = all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == 'Online')].usd.sum()
    online_22 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Online') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum()
    yoy_online = int(online_23-online_22)
    yoy_online_perc = round(int(online_23-online_22) / online_22,2)

    alt_23 = all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == 'Alternate Retail')].usd.sum()
    alt_22 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Alternate Retail') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum()
    yoy_alt = int(alt_23-alt_22)
    yoy_alt_perc = round(int(alt_23-alt_22) / alt_22,2)

    conv_23 = all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == 'Convenience')].usd.sum()
    conv_22 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Convenience') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum()
    yoy_conv = int(conv_23-conv_22)
    yoy_conv_perc = round(int(conv_23-conv_22) / conv_22,2)

    canada_23 = all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == 'Canada')].usd.sum()
    canada_22 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Canada') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum()
    yoy_canada = int(canada_23-canada_22)
    yoy_canada_perc = round(int(canada_23-canada_22) / (1 + canada_22),2)

    grocery_23 = all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == 'Grocery')].usd.sum()
    grocery_22 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Grocery') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum()
    yoy_grocery = int(grocery_23-grocery_22)
    yoy_grocery_perc = round(int(grocery_23-grocery_22) / grocery_22,2)

    broadline_23 = all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == 'Broadline Distributor')].usd.sum()
    broadline_22 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Broadline Distributor') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum()
    yoy_broadline = int(broadline_23-broadline_22)
    yoy_broadline_perc = round(int(broadline_23-broadline_22) / broadline_22,2)

    other_23 = all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == 'Other')].usd.sum()
    other_22 = all_sales[(all_sales['date'].dt.year == 2023) & (all_sales['market_segment'] == 'Other') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum()
    yoy_other = int(other_23-other_22)
    yoy_other_perc = round(int(other_23-other_22) / other_22,2)

    # METRICS BOXES
    blank, col1, col2, col3, col4, blank = st.columns([.5,2,2,2,2,.25])
    blank.markdown("")
    col1.metric(label='Vending', value=f"${int(vending_23):,}", delta = f"{yoy_vend_perc:.0%}")
    col2.metric(label='Online', value=f"${int(online_23):,}", delta = f"{yoy_online_perc:.0%}")
    col3.metric(label='Alternate Retail', value=f"${int(alt_23):,}", delta = f"{yoy_alt_perc:.0%}")
    col4.metric(label='Canada', value=f"${int(canada_23):,}", delta = f"{yoy_canada_perc:.0%}")
    blank.markdown("")
    st.markdown("##")
    st.markdown("##")
    blank, col1, col2, col3, col4, blank = st.columns([.5,2,2,2,2,.25])
    blank.markdown("")
    col1.metric(label='Convenience', value=f"${int(conv_23):,}", delta = f"{yoy_conv_perc:.0%}")
    col2.metric(label='Grocery', value=f"${int(grocery_23):,}", delta = f"{yoy_grocery_perc:.0%}")
    col3.metric(label='Broadline', value=f"${int(broadline_23):,}", delta = f"{yoy_broadline_perc:.0%}")
    col4.metric(label='Other', value=f"${int(other_23):,}", delta = f"{yoy_other_perc:.0%}")
    blank.markdown("")




# ---- REMOVE UNWANTED STREAMLIT STYLING ----
# hide_st_style = """
#             <style>
#             Main Menu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
            
# st.markdown(hide_st_style, unsafe_allow_html=True)