import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sqlalchemy import create_engine
import psycopg2
import secrets
import numpy as np
from datetime import datetime
from millify import millify


st.set_page_config(page_title='Awake YTD',
                   page_icon='assets/Nevil.png',
                   layout='centered'
)

alt.themes.enable("dark")
st.sidebar.title("AWAKE")

st.markdown("""
<style>
[data-testid="block-container"] {
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    # padding-left: 1rem;
    # padding-right: 5rem;
}

[data-testid="stMetric"] {
    border: 2px solid;
    border-radius: 10px;
    background-color: #e8e6e3;
    border-color: #B1A999;        
    text-align: center;
}

[data-testid="stMetricLabel"] {
display: flex;
justify-content: center;
align-items: center;
font-weight: 900;
}
            
[data-testid="stMetricValue"] {
font-size: 20px;
}

[data-testid="stMetricDeltaIcon-Up"] {
    color:  #009933;
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
            
[data-baseweb="tab-list"] {
    gap: 4px;
}

[data-baseweb="tab"] {
    height: 25px;
    width: 90px;
    white-space: pre-wrap;
    background-color: #A29F99;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 8px;
    padding-bottom: 8px;
}

[aria-selected="true"] {
    background-color: #A29F99;
}
        </style>
        """, unsafe_allow_html=True)

###############
# L2 CONNECTION
@st.cache_data
def get_connection():
    conn = st.connection('dot', type ="sql")
    all_sales = conn.query("SELECT * FROM level_2 WHERE date > '2022-12-31'")
    return all_sales

all_sales = get_connection()
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

origin_dict = {'unl':'Unleashed',
               'dot':'Dot'}

all_sales['sale_origin'] = all_sales['sale_origin'].map(origin_dict)

###############
# L1 CONNECTION
@st.cache_data
def get_connection2():
    conn2 = st.connection('dot', type ="sql")
    l1 = conn2.query("SELECT * FROM unleashed_raw WHERE completed_date > '2022-12-31';")
    return l1

l1 = get_connection2()
l1.completed_date = pd.to_datetime(l1.completed_date)
l1['usd'] = l1['sub_total']*.75


###############
# COLOR DICTIONARIES
market_segment_dict = {
    'Vending': 'rgb(56,149,73)',
    'Grocery': 'rgb(248,184,230)',
    'Alternate Retail': 'rgb(46,70,166)',
    'Canada': 'rgb(204,208,221)',
    'Online': 'rgb(106,87,63)',
    'Other': 'rgb(200,237,233)',
    'Convenience': 'rgb(233,81,46)',
    'Broadline Distributor': 'rgb(233,152,19)',
    'Samples': 'rgb(141,62,92)'}

sale_origin_dict = {
    'Dot': 'rgb(81, 121, 198)',
    'Unleashed': 'rgb(239, 83, 80)'
}

###############
# L1/L2 KPI'S
week_ago = datetime.today().date() - pd.offsets.Day(10)
recent_sales = all_sales[(all_sales.date>week_ago) & (all_sales.market_segment!='Samples')]
current_date = datetime.today().strftime('%Y-%m-%d')
import datetime
year_ago_today = datetime.datetime.today() - datetime.timedelta(days=365)

l1_sales_24 = int(l1[(l1['completed_date'] > '2023-12-31') & (l1['completed_date'] < current_date)].usd.sum())
l1_sales_23 = int(l1[(l1['completed_date'] > '2022-12-31') & (l1['completed_date'].dt.date < year_ago_today.date())].usd.sum())
l1_yoy_chg_perc = f"{(l1_sales_24/l1_sales_23-1)*100:.0f}%"

sales_24 = int(all_sales[(all_sales['date'] > '2023-12-31') & (all_sales['date'] < current_date)].usd.sum())
sales_23 = int(all_sales[(all_sales['date'] > '2022-12-31') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum())
yoy_chg_perc = f"{(sales_24/sales_23-1)*100:.0f}%"

#&nbsp
col0, col1, col2, col3= st.columns([1,2.1,2,2])
with col0:
    st.markdown("")
with col1:
    st.markdown(f"<h5>Direct Sales<br>&nbsp&nbsp&nbsp&nbsp<small>Dot as One</small></h5>", unsafe_allow_html=True)
    st.markdown(f"<h3><b>${l1_sales_24/1000000:.2f}</b>M<br>&nbsp&nbsp&nbsp&nbsp&nbsp<small>+{l1_yoy_chg_perc}</small></h3>", unsafe_allow_html=True)
    # st.markdown(f"<h5>&nbsp&nbsp&nbsp&nbsp&nbsp+{l1_yoy_chg_perc}</h5>", unsafe_allow_html=True)
with col2:
    st.image(r"assets/Nevil.png",width=65)
    st.caption(f"<h5>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbspytd</h5>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<h5>True Sales<br>&nbsp&nbsp<small>Dot as Many</small></h5>", unsafe_allow_html=True)
    st.markdown(f"<h3><b>${sales_24/1000000:.2f}M</b><br>&nbsp&nbsp&nbsp&nbsp&nbsp<small>+{yoy_chg_perc}</h3>", unsafe_allow_html=True)
    # st.markdown(f"<h5>&nbsp&nbsp&nbsp&nbsp&nbsp+{yoy_chg_perc}</h5>", unsafe_allow_html=True)

"---"

###################
# METRICS BOXES

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
# st.markdown("#")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label='Vending', value=f"${vending_23/1000:,.0f}K", delta = f"{yoy_vend_perc:.0%}")
col2.metric(label='Online', value=f"${millify(online_23)}", delta = f"{yoy_online_perc:.0%}")
col3.metric(label='Alternate Retail', value=f"${millify(alt_23)}", delta = f"{yoy_alt_perc:.0%}")
col4.metric(label='Canada', value=f"${millify(canada_23)}", delta = f"{yoy_canada_perc:.0%}")

col1, col2, col3, col4 = st.columns(4)
col1.metric(label='Convenience', value=f"${millify(conv_23)}", delta = f"{yoy_conv_perc:.0%}")
col2.metric(label='Grocery', value=f"${millify(grocery_23)}", delta = f"{yoy_grocery_perc:.0%}")
col3.metric(label='Broadline', value=f"${millify(broadline_23)}", delta = f"{yoy_broadline_perc:.0%}")
col4.metric(label='Other', value=f"${millify(other_23)}", delta = f"{yoy_other_perc:.0%}")

# DAILY BY MARKET SEGMENT
df = all_sales[all_sales.market_segment != 'Samples'].groupby([all_sales.date,'market_segment']).usd.sum().reset_index().set_index('date')
df = round(df[df.index>'2024-01-31']).sort_values(by='market_segment',ascending=False)#.sort_index())

chart_height = 235
config = {'displayModeBar': False}

scatter_market = px.bar(
    df,
    y='usd',
    template = 'plotly_white',
    labels={'date':'',
            'usd':''},
    height=chart_height,
    color='market_segment',
    color_discrete_map=market_segment_dict
)
scatter_market.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>')
scatter_market.update_coloraxes(showscale=False)
scatter_market.update_yaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[0,25000,50000,75000,100000],tickfont=dict(color='#5A5856', size=14),showticklabels=False)
scatter_market.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=25))
scatter_market.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
scatter_market.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),
                              showlegend=True,
                              legend=dict(orientation='h',
                                          yanchor="bottom",
                                          y=1,
                                          xanchor="center",
                                          x=.5,
                                          title='')
                                          )

# DAILY BY SALE CUSTOMER
df = all_sales[all_sales.market_segment != 'Samples'].groupby([all_sales.date,'parent_customer','market_segment']).usd.sum().reset_index().set_index('date')
df = round(df[df.index>'2024-01-31'].sort_index())

scatter_customer = px.scatter(
    df.reset_index(),
    x='date',
    y='usd',
    template = 'plotly_white',
    labels={'date':'','usd':''},
    height=chart_height,
    color='market_segment',
    color_discrete_map=market_segment_dict,
    log_y=True,
    opacity=.75,
    hover_name='parent_customer',
    hover_data = {'market_segment':False,
                  'usd':':.2s',
                  'date':False
                  }
)
scatter_customer.update_traces(marker=dict(size=14,opacity=.6,line=dict(width=1,color='lightgrey')),selector=dict(mode='markers'))
scatter_customer.update_coloraxes(showscale=False)
scatter_customer.update_yaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[100,1000,10000,100000,1000000],tickfont=dict(color='#5A5856', size=14),showticklabels=True)
scatter_customer.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=25))
scatter_customer.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
scatter_customer.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=False,)

# DAILY BY SALE ORIGIN
df = all_sales[all_sales.market_segment != 'Samples'].groupby([all_sales.date,'sale_origin']).usd.sum().reset_index().set_index('date')
df = round(df[df.index>'2024-01-31'].sort_index())

scatter_origin = px.bar(
        df,
        y='usd',
        template = 'plotly_white',
        labels={'date':'',
                'usd':''},
        height=chart_height,
        color='sale_origin',
        color_discrete_map=sale_origin_dict,
        text_auto='.2s',
        opacity=.75
    )

scatter_origin.update_traces(hovertemplate = 
    '$%{y:.2s}'+
    '<br>%{x:%Y-%m-%d}<br>')

scatter_origin.update_coloraxes(showscale=False)
scatter_origin.update_yaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[0,25000,50000,75000,100000],tickfont=dict(color='#5A5856', size=14),showticklabels=False)
scatter_origin.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=25))
scatter_origin.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
scatter_origin.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),showlegend=True,
                              legend=dict(orientation='h',
                                          yanchor="bottom",
                                          y=1,
                                          xanchor="right",
                                          x=.5,
                                          title=''))

# DAILY BY All (level 2)
df = all_sales[all_sales.market_segment != 'Samples'].groupby(all_sales.date).usd.sum().reset_index().set_index('date')
df = round(df[df.index>'2024-01-31'].sort_index())

bar_all = px.bar(
        df,
        y='usd',
        template = 'plotly_white',
        labels={'date':'',
                'usd':''},
        height=chart_height,
        text_auto='.2s',
    )
bar_all.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>')
bar_all.update_traces(marker_color='#E09641')
bar_all.update_coloraxes(showscale=False)
bar_all.update_yaxes(showticklabels=False,showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[0,25000,50000,75000,100000],tickfont=dict(color='#5A5856', size=14))
bar_all.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
bar_all.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
bar_all.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),)

# LEVEL 1 DAILY BAR
l1['usd'] = l1['sub_total']*.75

l1_bar_df = round(l1[l1.completed_date>'2024-01-31'].groupby('completed_date')['usd'].sum(),2).reset_index().set_index('completed_date')

level_1_bar = px.bar(l1_bar_df,
                     y='usd',
                     template='plotly_white',
                     labels={'usd':'',
                             'completed_date':''},
                     height=chart_height,
                     text_auto=",.2s")

level_1_bar.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>',marker_color='rgb(239, 83, 80)')
level_1_bar.update_coloraxes(showscale=False)
level_1_bar.update_yaxes(showticklabels=False,showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[0,25000,50000,75000,100000],tickfont=dict(color='#5A5856', size=14))
level_1_bar.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
level_1_bar.update_xaxes(tickmode='array',tickvals = l1_bar_df.index, ticktext=l1_bar_df.index.strftime('<b>%a<br>%d</b>'))
level_1_bar.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"))

l1_df = round(l1[l1.completed_date>'2024-01-31'][['completed_date','customer_name','product','usd']]).set_index('completed_date').sort_index(ascending=False)
true_df1 = round(all_sales[(all_sales.market_segment != 'Samples') & (all_sales.date>'2024-01-31')].drop(columns=['item','customer','qty','cad','month','year'])).reset_index(drop=True).set_index('date')
true_df2 = round(all_sales[(all_sales.market_segment != 'Samples') & (all_sales.date>'2024-01-31')].drop(columns=['item','customer','qty','cad','month','year'])).reset_index(drop=True).set_index('date')
true_df3 = round(all_sales[(all_sales.market_segment != 'Samples') & (all_sales.date>'2024-01-31')].drop(columns=['item','customer','qty','cad','month','year'])).reset_index(drop=True).set_index('date')



# st.markdown("")
st.markdown("<h5 style=text-align:center><br><b>February</b> - Daily</h5><br>",unsafe_allow_html=True)

tab0, tab1, tab2, tab3 = st.tabs(["Direct","TRUE", "TRUE - Source", "TRUE - Market"])
with tab0:
    st.plotly_chart(level_1_bar,config=config, use_container_width=True)
    st.caption('supporting data below')
    st.data_editor(l1_df,column_config={'completed_date':st.column_config.DateColumn('date', format='MM.DD.YYYY',step=1 )},use_container_width=True)
with tab1:
    st.plotly_chart(bar_all,config=config, use_container_width=True)
    st.caption('supporting data below')
    st.data_editor(true_df1,column_config={'date':st.column_config.DateColumn('date', format='MM.DD.YYYY',step=1 )},key='a',use_container_width=True)
with tab2:
    st.plotly_chart(scatter_origin,config=config, use_container_width=True)
    st.caption('supporting data below')
    st.data_editor(true_df2,column_config={'date':st.column_config.DateColumn('date', format='MM.DD.YYYY',step=1 )},key='b',use_container_width=True)
with tab3:
    st.plotly_chart(scatter_market,config=config, use_container_width=True)
    st.caption('supporting data below')
    st.data_editor(true_df3,column_config={'date':st.column_config.DateColumn('date', format='MM.DD.YYYY',step=1 )},key='c',use_container_width=True)




# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)