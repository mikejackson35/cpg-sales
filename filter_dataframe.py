import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sqlalchemy import create_engine
import psycopg2
import secrets
import numpy as np
from millify import millify
import plotly.graph_objects as go
from main_utils import market_legend_dict, market_segment_dict, sale_origin_dict

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.set_page_config(page_title='Charts',
                   page_icon=":bar_chart:",
                   layout='centered'
)

alt.themes.enable("dark")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
<style>
#         .block-container {
#             padding-top: 0rem;
#             padding-bottom: 0rem;
#             padding-left: 1rem;
#             padding-right: 1rem;
#         }
#         [data-baseweb="tab-list"] {
#         gap: 6px;
# }

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
    all_sales = conn.query("SELECT * FROM level_2 WHERE date > '2022-12-31'")
    return all_sales

all_sales = get_connection()
all_sales = all_sales[all_sales.market_segment != 'Samples']

st.markdown("#")

origin_dict = {'unl':'Unleashed',
               'dot':'Dot'}

all_sales['sale_origin'] = all_sales['sale_origin'].map(origin_dict)

# invoice date cleanup
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

unique_market_segments = list(all_sales.market_segment.unique())
unique_market_segments_sorted = sorted(filter(None, unique_market_segments))

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("click to filter")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or column == 'month' or column == 'parent_customer' or column == 'customer' or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

# df = all_sales.copy()
df = filter_dataframe(all_sales)

config = {'displayModeBar': False}
seg_sales = round(df.groupby('market_segment',as_index=False)['usd'].sum()).sort_values(by='market_segment',ascending=False)

fig_seg_sales = px.pie(
    seg_sales, 
    values='usd', 
    names='market_segment',
    template = 'plotly_dark',
    title=' ',
    opacity = .8,
    hole=.33,
    hover_name='market_segment',
    color='market_segment',
    color_discrete_map=market_segment_dict).update_layout(showlegend=False, autosize=True, width=450,height=450)

fig_seg_sales.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}<br>%{percent:.0%}',hovertemplate = '%{label}<br>%{value:.2s}')

## monthly bar chart
df.index = pd.to_datetime(df['date'])
mth_sales = round(df.groupby(pd.Grouper(freq='M'))[['usd']].sum())

fig_mth_bar = px.bar(mth_sales.reset_index(),
        template='plotly_dark',
        x= 'date',
        y='usd',
        labels = {'date':' ','usd':''},
        text='usd',
        opacity=.8,
        height=260,
        title='Monthly'
        ).update_coloraxes(showscale=False).update_layout(title_x=.4)
fig_mth_bar.update_traces(marker_color='#E09641',texttemplate='%{text:$,.2s}',hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')
fig_mth_bar.update_xaxes(showgrid=False,gridcolor='gray',tickvals = mth_sales.index,ticktext=mth_sales.index.strftime('%b-%y'),tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
fig_mth_bar.update_yaxes(showgrid=False,tick0=0,dtick=250000,showticklabels=False, tickcolor='darkgrey', gridcolor='darkgrey')   

# WEEKLY SCATTER CHART
df.index = pd.to_datetime(df['date'])
sales_per_week = df.groupby(pd.Grouper(freq='W'))['usd'].sum()

fig_scatter_all = px.scatter(
    round(sales_per_week),
    x=sales_per_week.index,
    y='usd',
    title='10-Wk Moving Avg',
    template = 'plotly_dark',
    labels={'date':'',
            'usd':''},
    height=260,
    color='usd',
    color_continuous_scale=px.colors.sequential.Oranges,
    trendline="rolling", trendline_options=dict(function="mean", window=10), trendline_scope="overall", trendline_color_override="grey"
)
fig_scatter_all.update_traces(name="",hovertemplate="Sales: <b>%{y:$,.0f}")
fig_scatter_all.update_traces(marker=dict(size=8,color='#E09641',opacity=.9,line=dict(width=1,color='lightgrey')),selector=dict(mode='markers'))
fig_scatter_all.update_coloraxes(showscale=False)
fig_scatter_all.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_scatter_all.update_layout(hovermode='x unified',showlegend=False,title_x=.4)#,legend=dict(y=0.99, x=0.1,title='10-Wk Moving Avg'))
fig_scatter_all.update_layout(hoverlabel=dict(font_size=15,font_family="Rockwell"))
fig_scatter_all.update_xaxes(showticklabels=True,showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=14),title_font=dict(color='#5A5856',size=15))
# fig_scatter_all.update_yaxes(tick0=0,dtick=250000)

###################
# tRUE YoY by Month Sales

all_sales['year'] = all_sales['date'].dt.year
all_sales['month'] = all_sales['date'].dt.month_name()

yoy_df = all_sales[all_sales['market_segment'].isin(df.market_segment) &
                   all_sales['sale_origin'].isin(df.sale_origin) &
                   all_sales['parent_customer'].isin(df.parent_customer) &
                   all_sales['customer'].isin(df.customer)
                   ].groupby(['year','month'],as_index=False)['usd'].sum()

sales_23_ = yoy_df[(yoy_df.year==2023)].usd
sales_24_ = yoy_df[yoy_df.year==2024].usd

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

color = yoy_df.year.astype('category').unique()

# Bar and scatter monthly
l2_fig = go.Figure(
    data=[
        go.Bar(x=months, y=sales_23_, name="2023", marker_color="#909497",textfont=dict(color='#D6D8CF'), marker_line_color="#909497", marker_opacity=.5,hovertemplate="<br>".join(["%{y:.2s}"])),#,textposition='outside'),
        go.Bar(x=months, y=sales_24_, name="2024", marker_color='#E09641',textfont=dict(color='white',size=25), marker_line_color="#E09641",hovertemplate="<br>".join(["%{y:.2s}"])),#,textposition='outside')
    ],
    layout=dict(title='YoY', title_x=.45, 
                height=260, 
                barmode='group', template='plotly_dark', 
                hoverlabel=dict(font_size=18,font_family="Rockwell"),
                legend=dict(x=0.02, y=1.5, orientation='h',font_color='#5A5856'),
                bargap=0.15,bargroupgap=0.1)
)

l2_fig.update_traces(texttemplate='$%{y:,.2s}')
l2_fig.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=25))
l2_fig.update_yaxes(showticklabels=False,showgrid=False,gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=13))

# distributor bar chart
top_custs = pd.DataFrame(df.groupby(['customer','market_segment'],as_index=False)['usd'].sum().sort_values(by='usd',ascending=False)[:40])
fig_dist_sales = px.bar(top_custs,
       x = 'customer',
       y = 'usd',
       title='Top Individual Customers',
    template = 'plotly_dark',
    labels={'customer':'',
            'usd':' '},
    opacity=.8,
    height=400, 
    color = 'market_segment',
    text = 'usd',
    color_discrete_map=market_segment_dict).update_layout(showlegend=False,title_x=.4)
fig_dist_sales.update_yaxes(tick0=0,dtick=500000)
fig_dist_sales.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_dist_sales.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=11),title_font=dict(color='#5A5856',size=15))#,tickangle=30)
fig_dist_sales.update_traces(texttemplate='%{text:$,.2s}',hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')#,textposition='outside')


# parent distributor bar
top_parents = pd.DataFrame(df.groupby(['parent_customer','market_segment'],as_index=False)['usd'].sum().sort_values(by='usd',ascending=False)[:15])
fig_parent_sales = px.bar(top_parents,
                          x = 'parent_customer',
                          y = 'usd',
                          title='Top Parent Customers',
                          template = 'plotly_dark',
                          labels={'parent_customer':'',
                                'usd':''},
                          height=350,
                          opacity = .8,
                          color = 'market_segment',
                          text = 'usd',
                          color_discrete_map=market_segment_dict).update_layout(showlegend=False,title_x=.4)
fig_parent_sales.update_yaxes(tick0=0,dtick=1000000)
fig_parent_sales.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')
fig_parent_sales.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_parent_sales.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
fig_parent_sales.update_traces(texttemplate='%{text:$,.2s}')

start = df.date.min().date()
end = df.date.max().date()

col1, col2 = st.columns(2)
with col1:
    st.markdown("###")
    st.markdown("###")
    st.markdown("###")
    st.markdown("###")
    # df = filter_dataframe(all_sales)
    st.markdown("<h2>tRUE Sales</h2>",unsafe_allow_html=True)
    st.markdown(f"<h4><b>${millify(df.usd.sum(),precision=1)}</b><br><br><b>{start}</b> <br><small>thru</small><br><b>{end}</b>",unsafe_allow_html=True)
    # st.markdown("#")
with col2:
    st.plotly_chart(fig_seg_sales,config=config,use_container_width=True)

tab1, tab2, tab3 = st.tabs(["Monthly", "Weekly", "YoY"])
with tab1:
    st.plotly_chart(fig_mth_bar, config=config,legend=None, use_container_width=True)
with tab2:
    st.plotly_chart(fig_scatter_all, config=config,use_container_width=True)
with tab3:
    st.plotly_chart(l2_fig, config=config,use_container_width=True)

tab1, tab2 = st.tabs(["by Parent", "by Customer"])
with tab1:
    st.plotly_chart(fig_parent_sales,config=config, use_container_width=True)
with tab2:
    st.plotly_chart(fig_dist_sales,config=config, use_container_width=True)
