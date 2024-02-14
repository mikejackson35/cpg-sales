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
                #    layout='wide'
)

alt.themes.enable("dark")

#######################
# CSS styling for metrics
st.markdown("""
<style>

[data-testid="block-container"] {
    # padding-left: 18rem;
    # padding-right: 22rem;
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
    text-align: center;
    padding-right: 12px 0;
    padding-left: 12px 0;
    
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 900;
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
    gap: 6px;
}

[data-baseweb="tab"] {
    height: 30px;
    width: 80px;
    white-space: pre-wrap;
    # background-color: #BFB3A0;
    background-color: #A29F99;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
}

[aria-selected="true"] {
    background-color: #A29F99;
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

# LOGO AND TITLE
st.sidebar.title("AWAKE")

# col1, col2 = st.columns([3,1])

# # with blank:
# #     st.markdown("####")

# with col2:
######################
week_ago = datetime.today().date() - pd.offsets.Day(10)
recent_sales = all_sales[all_sales.date>week_ago]
config = {'displayModeBar': False}

    # daily sales scatter colored by sales_origin
df = recent_sales.groupby(recent_sales.date).usd.sum().reset_index().set_index('date')
    # fig = px.scatter(df,
    #        x='usd',
    #        labels={'date':"", 'usd':''},
    #        height=750,
    #        width=300,
    #        template='plotly_white',
    #     #    text=round(df.usd),
    #       )
    # fig.update_traces(marker=dict(size=35,color='#E09641',line=dict(width=1,color='grey')),selector=dict(mode='markers'),hovertemplate ="<b>$%{x:,.2s}</b>")
    # fig.update_xaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[0,25000,50000,75000,100000],tickfont=dict(color='#5A5856', size=15),showticklabels=True)
    # fig.update_yaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=18))
    # fig.update_layout(xaxis={'side':'top'},legend=dict(title=''),coloraxis_showscale=False)
    # # fig.update_layout(yaxis=dict(type = 'category'))
    # fig.update_yaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('%a  %b-%d'))

    # # daily sales scatter colored by sales_origin
    # fig1 = px.scatter(recent_sales.groupby([recent_sales.date,'sale_origin']).usd.sum().reset_index().set_index('date'),
    #        x='usd',
    #        color='sale_origin',
    #        color_discrete_map={'unl':"#E62F29",'dot':"#3A4DA1"},
    #        opacity=.8,
    #        labels={'date':"", 'usd':''},
    #        height=750,
    #        width=300,
    #        template='plotly_white',
    #        hover_name='sale_origin',
    #       ).update_layout(showlegend=False)
    # fig1.update_traces(marker=dict(size=30,line=dict(width=1,color='grey')),selector=dict(mode='markers'),hovertemplate ="<b>$%{x:,.2s}</b>")
    # fig1.update_xaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[0,25000,50000,75000,100000],tickfont=dict(color='#5A5856', size=15), showticklabels=True)
    # fig1.update_yaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=18))
    # fig1.update_layout(xaxis={'side':'top'})
    # # fig1.update_layout(yaxis=dict(type = 'category'))
    # fig1.update_yaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('%a  %b-%d'))

    # # daily sales scatter colored by 'market_segment
    # fig2 = px.scatter(recent_sales.groupby([recent_sales.date,'market_segment']).usd.sum().reset_index().set_index('date'),
    #        x='usd',
    #        color='market_segment',
    #        color_discrete_map=market_segment_dict,
    #        opacity=.7,
    #        labels={'date':"", 'usd':''},
    #        height=750,
    #     #    width=300,
    #        template='plotly_white',
    #        hover_name='market_segment',
    #        log_x=True
    #       ).update_layout(showlegend=False)
    # fig2.update_traces(marker=dict(size=20,line=dict(width=2,color='grey')),selector=dict(mode='markers'),hovertemplate ="<b>$%{x:,.2s}</b>")
    # fig2.update_xaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[100,1000,10000,100000],tickfont=dict(color='#5A5856', size=15),showticklabels=True)
    # fig2.update_yaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=18))
    # fig2.update_layout(xaxis={'side':'top'},legend=dict(title=''))
    # # fig2.update_layout(yaxis=dict(type = 'category'))
    # fig2.update_yaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('%a  %b-%d'))

    # # daily sales scatter colored by parent_customer
    # fig3 = px.scatter(recent_sales.groupby([recent_sales.date,'parent_customer','market_segment']).usd.sum().reset_index().set_index('date'),
    #        x='usd',
    #        color='market_segment',
    #        color_discrete_map=market_segment_dict,
    #        opacity=.8,
    #        labels={'date':"", 'usd':''},
    #        height=750,
    #     #    width=300,
    #        template='plotly_white',
    #        hover_name='parent_customer',
    #        log_x = True
    #       ).update_layout(showlegend=False)
    # fig3.update_traces(marker=dict(size=15,line=dict(width=2,color='grey')),selector=dict(mode='markers'))
    # fig3.update_xaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[100,1000,10000,100000],tickfont=dict(color='#5A5856', size=15),showticklabels=True)
    # fig3.update_yaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=18))
    # fig3.update_layout(xaxis={'side':'top'},legend=dict(title=''))
    # # fig3.update_layout(yaxis=dict(type = 'category'))
    # fig3.update_yaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('%a  %b-%d'))
    
    # st.markdown("####")
    # st.subheader("Recent Daily Sales")
    # st.caption("choose aggregation...")
    
    # tab, tab1, tab2, tab3 = st.tabs(["All Sales", "Dot/Direct", "Segment", "Customer"])

    # with tab:
    #     st.plotly_chart(fig,config=config,use_container_width=True)
    # with tab1:
    #     st.plotly_chart(fig1,config=config,use_container_width=True)
    # with tab2:
    #     st.plotly_chart(fig2,config=config,use_container_width=True)
    # with tab3:
    #     st.plotly_chart(fig3,config=config,use_container_width=True)
        

# with col1:
    # st.markdown("<h1 style='text-align: center;'>AWAKE 2024</h1>", unsafe_allow_html=True)
st.markdown("")
# CALCS FOR KPI'S
current_date = datetime.today().strftime('%Y-%m-%d')
import datetime
year_ago_today = datetime.datetime.today() - datetime.timedelta(days=365)

sales_24 = int(all_sales[(all_sales['date'] > '2023-12-31') & (all_sales['date'] < current_date)].usd.sum())
sales_23 = int(all_sales[(all_sales['date'] > '2022-12-31') & (all_sales['date'].dt.date < year_ago_today.date())].usd.sum())

yoy_chg_perc = f"{(sales_24/sales_23-1)*100:.0f}%"

# TOP KPI'S
blank1, col1, blank2, col2 = st.columns([.6,1,1,1])
with blank1:
    st.markdown("")
with col1:
    st.markdown('<h4>Sales YTD</h4>', unsafe_allow_html=True)
    st.title(f"${sales_24/1000000:.2f}M")
with blank2:
    st.image(r"assets/Nevil.png",width=125)
with col2:
    st.markdown('<h4>YoY Change</h4>', unsafe_allow_html=True)
    st.title(f"+{yoy_chg_perc}")

# line divider & sub-title
# st.markdown("####")
# st.markdown("####")
# st.markdown("<b><h3 style='text-align: center;'>Market Segments</h3></b>", unsafe_allow_html=True)

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
st.markdown("#")
col1, col2, col3, col4 = st.columns([2,2,2,2])
# blank.markdown("")
col1.metric(label='Vending', value=f"${vending_23/1000:,.0f}K", delta = f"{yoy_vend_perc:.0%}")
# col1.metric(label='Vending', value=f"${millify(vending_23)}", delta = f"{yoy_vend_perc:.0%}")
col2.metric(label='Online', value=f"${millify(online_23)}", delta = f"{yoy_online_perc:.0%}")
col3.metric(label='Alternate Retail', value=f"${millify(alt_23)}", delta = f"{yoy_alt_perc:.0%}")
col4.metric(label='Canada', value=f"${millify(canada_23)}", delta = f"{yoy_canada_perc:.0%}")
# blank.markdown("")
# st.markdown("##")
# st.markdown("##")
col1, col2, col3, col4 = st.columns([2,2,2,2])
# blank.markdown("")
col1.metric(label='Convenience', value=f"${millify(conv_23)}", delta = f"{yoy_conv_perc:.0%}")
col2.metric(label='Grocery', value=f"${millify(grocery_23)}", delta = f"{yoy_grocery_perc:.0%}")
col3.metric(label='Broadline', value=f"${millify(broadline_23)}", delta = f"{yoy_broadline_perc:.0%}")
col4.metric(label='Other', value=f"${millify(other_23)}", delta = f"{yoy_other_perc:.0%}")
st.markdown("---")
st.markdown("")

# DAILY SALES HORIZONTAL SCATTER (XAXIS = CATEGORY)

df = all_sales.groupby([all_sales.date,'market_segment']).usd.sum().reset_index().set_index('date')
df = round(df[df.index>'2024-01-31'].sort_index())

fig_scatter_all = px.scatter(
    df,
    y='usd',
    template = 'plotly_white',
    labels={'date':'',
            'usd':''},
    height=325,
    color='market_segment',
    color_discrete_map=market_segment_dict,
    title='February',
    log_y=True
)

# df = all_sales.groupby([all_sales.date,'sale_origin']).usd.sum().reset_index().set_index('date')
# df = round(df[df.index>'2024-01-31'].sort_index())

# fig_scatter_all = px.scatter(
#         df,
#         y='usd',
#         template = 'plotly_white',
#         labels={'date':'',
#                 'usd':''},
#         height=325,
#         color='sale_origin',
#         # color_discrete_map='sale_origin',
#         title='February',
#         log_y=True
#     )

fig_scatter_all.update_traces(hovertemplate = 
    '$%{y:.2s}'+
    '<br>%{x:%Y-%m-%d}<br>')

fig_scatter_all.update_traces(marker=dict(size=14,opacity=.7,line=dict(width=1,color='grey')),selector=dict(mode='markers'))

fig_scatter_all.update_coloraxes(showscale=False)
fig_scatter_all.update_yaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[100,1000,10000,100000,1000000],tickfont=dict(color='#5A5856', size=17),showticklabels=True)
fig_scatter_all.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=15))
fig_scatter_all.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
fig_scatter_all.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),
                              title=dict(font=dict(size=22)),
                              showlegend=True,
                              title_x=.02,
                              title_y=.99,
                              legend=dict(orientation='h',
                                          yanchor="bottom",
                                          y=1.5,
                                          xanchor="right",
                                          x=1,
                                          title=''))

st.plotly_chart(fig_scatter_all,config=config, use_container_width=True)




# ---- REMOVE UNWANTED STREAMLIT STYLING ----
# hide_st_style = """
#             <style>
#             Main Menu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
            
# st.markdown(hide_st_style, unsafe_allow_html=True)