import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sqlalchemy import create_engine
import psycopg2
import secrets
import numpy as np
from millify import millify


st.set_page_config(page_title='Charts',
                   page_icon=":bar_chart:",
                   layout='centered'
)

alt.themes.enable("dark")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
<style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        [data-baseweb="tab-list"] {
        gap: 6px;
}

[data-baseweb="tab"] {
    height: 25px;
    width: 80px;
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

# ---- PULL IN DATA FROM POSTGRES DB ----
@st.cache_data
def get_connection():
    conn = st.connection('dot', type ="sql")
    all_sales = conn.query("SELECT * FROM level_2 WHERE date > '2021-12-31'")
    return all_sales

all_sales = get_connection()
all_sales = all_sales[all_sales.market_segment != 'Samples']
origin_dict = {'unl':'Unleashed',
               'dot':'Dot'}

all_sales['sale_origin'] = all_sales['sale_origin'].map(origin_dict)

# invoice date cleanup
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

# --- FILTERS AND SIDEBAR ----
year = st.sidebar.multiselect(
    label = 'Year',
    options=sorted(list(all_sales['year'].unique())),
    default=sorted(list(all_sales['year'].unique()))
)
sale_origin = st.sidebar.multiselect(
    label = 'Direct or Dot',
    options=np.array(all_sales['sale_origin'].unique()),
    default=np.array(all_sales['sale_origin'].unique()),
)
segment = st.sidebar.multiselect(
    label='Market Segment',
    options=np.array(all_sales['market_segment'].unique()),
    default=np.array(all_sales['market_segment'].unique()),
)

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

# sale_origin_dict = {
#     'Dot': 'rgb(81, 121, 198)',
#     'Unleashed': 'rgb(239, 83, 80)'
# }

# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = all_sales[
    (all_sales['year'].isin(year)) &
    (all_sales['market_segment'].isin(segment)) &
    (all_sales['sale_origin'].isin(sale_origin))
    ]

# # top row
# def plus_minus(delta):
#     if delta > 0:
#         symbol = "+"
#     else:
#         symbol = ""
#     return symbol

customer_count = int(df_selection.customer.nunique())
sales = int(df_selection.usd.sum())
mean_sales = int(sales/customer_count)

config = {'displayModeBar': False}
seg_sales = round(df_selection.groupby('market_segment',as_index=False)['usd'].sum()).sort_values(by='market_segment',ascending=False)

fig_seg_sales = px.pie(
    seg_sales, 
    values='usd', 
    names='market_segment',
    template = 'simple_white',
    title=' ',
    opacity = .8,
    hole=.33,
    hover_name='market_segment',
    color='market_segment',
    color_discrete_map=market_segment_color).update_layout(showlegend=False, autosize=True, width=350,height=350)
fig_seg_sales.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}<br>%{percent:.0%}')#,hovertemplate = '$%{values:.2s}'+'<br>%{x:%Y-%m}<br>')

## monthly bar chart
df_selection.index = pd.to_datetime(df_selection['date'],format = '%m/%y')
mth_sales = round(df_selection.groupby(pd.Grouper(freq='M'))['usd'].sum())

fig_mth_bar = px.bar(mth_sales.reset_index(),
        template='plotly_white',
        x= 'date',
        y='usd',
        labels = {'date':' ','usd':''},
        text='usd',
        opacity=.8,
        height=250
        ).update_coloraxes(showscale=False).update_traces(texttemplate='%{text:$,.2s}')#,textposition='outside')
fig_mth_bar.update_traces(marker_color='#E09641')
fig_mth_bar.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')
fig_mth_bar.update_xaxes(showgrid=False,gridcolor='gray',tickvals = mth_sales.index,ticktext=mth_sales.index.strftime('%b-%y'),tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
fig_mth_bar.update_yaxes(showgrid=False,tick0=0,dtick=250000,showticklabels=False, tickcolor='darkgrey', gridcolor='darkgrey')   

# WEEKLY SCATTER CHART
df_selection.index = pd.to_datetime(df_selection['date'],format = '%y/%m/%d')
sales_per_week = df_selection.groupby(pd.Grouper(freq='W'))['usd'].sum()

fig_scatter_all = px.scatter(
    round(sales_per_week),
    x=sales_per_week.index,
    y='usd',
    template = 'plotly_white',
    labels={'date':'',
            'usd':''},
    height=260,
    color='usd',
    color_continuous_scale=px.colors.sequential.Oranges,
    trendline="rolling", trendline_options=dict(function="mean", window=10), trendline_scope="overall", trendline_color_override="grey"
)
fig_scatter_all.update_traces(name="",hovertemplate="Sales: <b>%{y:$,.0f}")
fig_scatter_all.update_traces(marker=dict(size=10,color='#E09641',opacity=.9,line=dict(width=1,color='lightgrey')),selector=dict(mode='markers'))
fig_scatter_all.update_coloraxes(showscale=False)
fig_scatter_all.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_scatter_all.update_layout(hovermode='x unified',showlegend=False)#,legend=dict(y=0.99, x=0.1,title='10-Wk Moving Avg'))
fig_scatter_all.update_layout(hoverlabel=dict(font_size=15,font_family="Rockwell"))
fig_scatter_all.update_xaxes(showticklabels=True,showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=14),title_font=dict(color='#5A5856',size=15))
fig_scatter_all.update_yaxes(tick0=0,dtick=100000)

# distributor bar chart
top_custs = pd.DataFrame(df_selection.groupby(['customer','market_segment'],as_index=False)['usd'].sum().sort_values(by='usd',ascending=False)[:40])
fig_dist_sales = px.bar(top_custs,
       x = 'customer',
       y = 'usd',
    template = 'plotly_white',
    labels={'customer':'',
            'usd':' '},
    opacity=.8,
    height=400,
    # width=1000,        
    color = 'market_segment',
    text = 'usd',
    color_discrete_map=market_segment_color).update_layout(showlegend=False)
fig_dist_sales.update_yaxes(tick0=0,dtick=500000)
fig_dist_sales.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_dist_sales.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=11),title_font=dict(color='#5A5856',size=15))#,tickangle=30)
fig_dist_sales.update_traces(texttemplate='%{text:$,.2s}',hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')#,textposition='outside')


# parent distributor bar
top_parents = pd.DataFrame(df_selection.groupby(['parent_customer','market_segment'],as_index=False)['usd'].sum().sort_values(by='usd',ascending=False)[:15])
fig_parent_sales = px.bar(top_parents,
                          x = 'parent_customer',
                          y = 'usd',
                          template = 'plotly_white',
                          labels={'parent_customer':'',
                                'usd':''},
                          height=350,
                          opacity = .8,
                          color = 'market_segment',
                          text = 'usd',
                          color_discrete_map=market_segment_color).update_layout(showlegend=False)
fig_parent_sales.update_yaxes(tick0=0,dtick=1000000)
fig_parent_sales.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')
fig_parent_sales.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_parent_sales.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
fig_parent_sales.update_traces(texttemplate='%{text:$,.2s}')#,textposition='outside')


# st.header(f"${round(df_selection.usd.sum())}")
st.header(f"${millify(df_selection.usd.sum(),precision=1)}")
col3, col2, col1 = st.columns([2,.25,1])
with col1:
    st.plotly_chart(fig_seg_sales,config=config,use_container_width=True)
with col2:
    st.markdown("")
with col3:
    tab1, tab2 = st.tabs(["Monthly", "Weekly"])
    with tab1:
        st.plotly_chart(fig_mth_bar, config=config,legend=None, use_container_width=True)
    with tab2:
        st.plotly_chart(fig_scatter_all, config=config,use_container_width=True)

tab1, tab2 = st.tabs(["by Parent", "by Customer"])
with tab1:
    st.plotly_chart(fig_parent_sales,config=config, use_container_width=True)
with tab2:
    st.plotly_chart(fig_dist_sales,config=config, use_container_width=True)


# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)