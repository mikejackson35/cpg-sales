import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sqlalchemy import create_engine
import secrets
import numpy as np


st.set_page_config(page_title='Charts',
                   page_icon=":bar_chart:",
                   layout='wide'
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
        </style>
        """, unsafe_allow_html=True)

## ----- CONNECT TO POSTGRESQL DATABASE --------
connection_string = f"postgresql://{st.secrets['db_user']}:{st.secrets['db_password']}@{st.secrets['endpoint']}:5432/{st.secrets['db_name']}"
engine = create_engine(connection_string)

# ---- PULL IN DATA ----
@st.cache_data
def get_data_from_csv():
    # df = pd.read_sql("SELECT * FROM level_2 WHERE date > '2019-12-31'",con = engine)
    df = pd.read_csv(r"C:\Users\mikej\Desktop\cpg-sales\data\all_sales_data.csv")
    return df
all_sales = get_data_from_csv()

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
segment = st.sidebar.multiselect(
    label='Market Segment',
    options=np.array(all_sales['market_segment'].unique()),
    default=np.array(all_sales['market_segment'].unique()),
)

# line divider
st.markdown(" ")

# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = all_sales[
    (all_sales['year'].isin(year)) &
    (all_sales['market_segment'].isin(segment))
    ]

# theme used for charts
template = 'presentation'

# ---- TOP KPI's Row ----

def plus_minus(delta):
    if delta > 0:
        symbol = "+"
    else:
        symbol = ""
    return symbol

customer_count = int(df_selection.customer.nunique())
sales = int(df_selection.usd.sum())
mean_sales = int(sales/customer_count)



blank, col1, col2, col3 = st.columns([.25,1.2,1.2,1.2])
with blank:
    st.markdown(" ")
with col1:
    st.markdown('<h4>Sales</h4>', unsafe_allow_html=True)
    st.title(f"${int(df_selection.usd.sum()):,}")
with col2:
    st.markdown('<h4>Num of customers</h4>', unsafe_allow_html=True)
    st.title(F"{customer_count:,}")
with col3:
    st.markdown('<h4>$/customer</h4>', unsafe_allow_html=True)
    st.title(f"${mean_sales:,}")




############

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


df_selection.index = pd.to_datetime(df_selection['date'],format = '%m/%d/%y')
mth_sales = round(df_selection.groupby(pd.Grouper(freq='M'))['usd'].sum())

fig_mth_bar = px.bar(mth_sales,
        template=template,
        x= mth_sales.index,
        y='usd',
        color='usd',
        color_continuous_scale=px.colors.sequential.Oranges,
        labels = {'date':' ','usd':'<b>$USD</b>'},
        text='usd',
        opacity=.8,
        hover_data=['usd'],
        title='Monthly Sales',
        height=400
        ).update_coloraxes(showscale=False)
fig_mth_bar.update_traces(texttemplate='<b>%{text:$,}</b>',hovertext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
fig_mth_bar.update_layout(title_x=0.5)
fig_mth_bar.update_xaxes(tickmode='array',tickvals = mth_sales.index, ticktext=mth_sales.index.month_name())
fig_mth_bar.update_yaxes(tick0=0,dtick=250000,showticklabels=False, gridcolor='darkgrey')   

# line divider
st.markdown("   ")
st.markdown("---")
st.markdown("   ")

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
    hover_data = ['market_segment'],
    color='market_segment',
    color_discrete_map=market_segment_color).update_layout(autosize=False,width=450,height=450,showlegend=False)
fig_seg_sales.update_traces(textposition='inside', textinfo='percent+label')

space, pie, space, bar = st.columns([.25,1,.25,3.5])
with space:
    st.markdown(" ")
with pie:
    st.plotly_chart(fig_seg_sales, theme='streamlit', use_container_width=True)
with space:
    st.markdown(" ")
with bar:
    st.plotly_chart(fig_mth_bar, config=config,legend=None, use_container_width=True)

# line divider
st.markdown("   ")
st.markdown("---")
st.markdown("   ")

# distributor bar
top_custs = pd.DataFrame(df_selection.groupby(['customer','market_segment'],as_index=False)['usd'].sum().sort_values(by='usd',ascending=False)[:40])
fig_dist_sales = px.bar(top_custs,
       x = 'customer',
       y = 'usd',
    title='<b>Top Individual customers</b>',
    height=600,
    template = template,
    labels={'customer':'',
            'usd':'<b>$USD</b>'},
    opacity=.8,        
    color = 'market_segment',
    text_auto=',.0f',
    color_discrete_map=market_segment_color).update_layout(showlegend=False,title_x=0.5)#,margin=dict(l=20, r=20, t=80, b=20),paper_bgcolor="LightGrey")
fig_dist_sales.update_yaxes(tick0=0,dtick=500000).update_yaxes(gridcolor='lightgray')

# parent distributor bar
top_parents = pd.DataFrame(df_selection.groupby(['parent_customer','market_segment'],as_index=False)['usd'].sum().sort_values(by='usd',ascending=False)[:20])
fig_parent_sales = px.bar(top_parents,
                          x = 'parent_customer',
                          y = 'usd',
                          title='<b>Top Parent customers</b>',
                          template = template,
                          labels={'parent_customer':'',
                                'usd':'<b>$USD</b>'},
                          height=500,
                          opacity = .8,
                          color = 'market_segment',
                          text_auto=',.0f',
                          color_discrete_map=market_segment_color).update_layout(showlegend=False, title_x=0.5)#,margin=dict(l=20, r=20, t=80, b=20),paper_bgcolor="LightGrey")
fig_parent_sales.update_yaxes(tick0=0,dtick=1000000).update_yaxes(gridwidth=1,gridcolor='lightgray')


blank,bar,blank = st.columns([.5,3,.5])

with blank:
    st.markdown(" ")
with bar:
    customer_level = st.radio("Customer Level",
                            ['Parent Customer', 'Individual Customer'],
                            index=None, label_visibility='hidden', horizontal = True)

    if customer_level == 'Parent Customer':
        st.plotly_chart(fig_parent_sales, theme = 'streamlit', use_container_width=True)
    else:
        st.plotly_chart(fig_dist_sales, theme = 'streamlit', use_container_width=True)
with blank:
    st.markdown(" ")

# line divider
st.markdown("---")

# WEEKLY SCATTER CHARTS
df_selection.index = pd.to_datetime(df_selection['date'],format = '%y/%m/%d')
sales_per_week = df_selection.groupby(pd.Grouper(freq='W'))['usd'].sum()

#all sales weekly scatter
fig_scatter_all = px.scatter(
    sales_per_week,
    x=sales_per_week.index,
    y='usd',
    title='<b>Weekly Sales</b>',
    template = template,
    labels={'date':'',
            'usd':'<b>$USD</b>'},
    height=425,
    size='usd',
    size_max=15,
    # hover_name='usd',
    trendline="rolling", trendline_options=dict(function="mean", window=10), trendline_scope="overall", trendline_color_override="black"
).update_layout(title_x=0.4,hovermode='x').update_yaxes(gridcolor='lightgray')#.update_traces(hovertemplate="%{sales_per_week.index}")

fig_scatter_all.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        # title = '10 Week Moving Average'
    )
)

blank_left, scatter, blank_right,  = st.columns([.5,2.8,.5])
with blank:
    st.markdown(" ")
with scatter:
    st.plotly_chart(fig_scatter_all, theme = 'streamlit', use_container_width=True)
with blank:
    st.markdown(" ")

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)