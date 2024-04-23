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
import plotly.graph_objects as go
from main_utils import market_segment_dict, sale_origin_dict, market_legend_dict


st.set_page_config(page_title='Awake YTD',
                   page_icon='assets/Nevil.png',
                   layout='centered'
)
config = {'displayModeBar': False}

alt.themes.enable("dark")

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
config = {'displayModeBar': False}

# 'placeholder for 'updated on:' sidebar
updated = st.sidebar.empty()

###############
# L2 CONNECTION
# @st.cache_data
# def get_connection():
#     conn = st.connection('dot', type ="sql")
#     all_sales = conn.query("SELECT * FROM level_2 WHERE date > '2022-12-31'")
#     return all_sales

# all_sales = get_connection()
all_sales = pd.read_csv(r"level_2.csv", encoding='utf-8')
all_sales['date'] = pd.to_datetime(all_sales['date'])
all_sales['date'] = all_sales['date'].dt.normalize()
all_sales['date'] = all_sales['date'].dt.floor('D')

origin_dict = {'unl':'Unleashed',
               'dot':'Dot'}

all_sales['sale_origin'] = all_sales['sale_origin'].map(origin_dict)

###############
# L1 CONNECTION
# @st.cache_data
# def get_connection2():
#     conn2 = st.connection('dot', type ="sql")
#     l1 = conn2.query("SELECT * FROM unleashed_raw WHERE completed_date > '2022-12-31';")
#     return l1

# l1 = get_connection2()
l1 = pd.read_csv(r"C:\Users\mikej\Desktop\cpg-sales\data\level_1.csv")

l1.completed_date = pd.to_datetime(l1.completed_date)
# l1['usd'] = l1['sub_total']*.75

###############
# L1/L2 KPI'S

with updated:
    st.markdown(f"thru: {all_sales.date.max().strftime('%a %B %d')}", unsafe_allow_html=True)

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

all_sales['date'] = pd.to_datetime(all_sales['date'])

###################
# L1 Main Bar
l1_main_bar = l1[(l1.customer_type != 'Samples')][['completed_date','usd']].sort_values(by='completed_date',ascending=False)
l1_main_bar['year'] = l1_main_bar['completed_date'].dt.year
l1_main_bar['YearMonth'] = l1_main_bar['completed_date'].astype('string').apply(lambda x: x.split("-")[0] + "-" + x.split("-")[1])

l1_main_bar = l1_main_bar.groupby(['year','YearMonth'],as_index=False)['usd'].sum()

l1_23 = l1_main_bar[l1_main_bar.year==2023].usd
l1_24 = l1_main_bar[l1_main_bar.year==2024].usd
goal = l1_23 * 1.5

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

color = l1_main_bar.year.astype('category').unique()

l1_fig = go.Figure(
    data=[
        go.Scatter(x=months, y=goal, name="Direct Goal", mode='markers', marker_symbol='line-ew',marker_size=10, marker_line=dict(width=1,color='#5A5856'),marker_color='orange',hovertemplate="<br>".join(["%{y:.2s}"])),
        go.Bar(x=months, y=l1_23, name="2023", marker_color="#909497",textfont=dict(color='#D6D8CF'), marker_line_color="#909497", marker_opacity=.5,hovertemplate="<br>".join(["%{y:.3s}"]),textposition='outside'),
        go.Bar(x=months, y=l1_24, name="2024", marker_color='#5A5856',textfont=dict(color='white'), marker_line_color="#5A5856",hovertemplate="<br>".join(["%{y:.3s}"]),textposition='outside')
    ],
    layout=dict(#title='2024', title_x=.45, 
                height=300, 
                barmode='group', template='plotly_dark', 
                hoverlabel=dict(font_size=18,font_family="Rockwell"),
                legend=dict(x=0.02, y=1.5, orientation='h',font_color='#5A5856'),
                bargap=0.15,bargroupgap=0.1)
)

l1_fig.update_traces(texttemplate='%{y:.3s}')
l1_fig.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=15),title_font=dict(color='#5A5856',size=25))
l1_fig.update_yaxes(showticklabels=False,showgrid=True,gridcolor="#B1A999")


###################
# L2 Main Bar
# def getYearMonth(s):
#   return (s.split("-")[0] + "-" + s.split("-")[1])

all_sales['year'] = all_sales['date'].dt.year
all_sales['month'] = all_sales['date'].dt.month_name()
all_sales['YearMonth'] = all_sales['date'].astype('string').apply(lambda x: x.split("-")[0] + "-" + x.split("-")[1])

# group by month year and add $0 sales to future months
chart_df = round(all_sales.groupby(['year','YearMonth'],as_index=False)['usd'].sum())

sales_22_ = chart_df[chart_df.year==2022].usd
sales_23_ = chart_df[chart_df.year==2023].usd
sales_24_ = chart_df[chart_df.year==2024].usd

goal = sales_23_ * 1.5

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

color = chart_df.year.astype('category').unique()

# Bar and scatter monthly
l2_fig = go.Figure(
    data=[
        go.Scatter(x=months, y=goal, name="TRUE Goal", mode='markers', marker_symbol='line-ew',marker_size=10, marker_line=dict(width=1,color='#5A5856'),marker_color='orange',hovertemplate="<br>".join(["%{y:.2s}"])),
        go.Bar(x=months, y=sales_23_, name="2023", marker_color="#909497",textfont=dict(color='#D6D8CF'), marker_line_color="#909497", marker_opacity=.5,hovertemplate="<br>".join(["%{y:.2s}"]),textposition='outside'),
        go.Bar(x=months, y=sales_24_, name="2024", marker_color='#E09641',textfont=dict(color='white',size=25), marker_line_color="#E09641",hovertemplate="<br>".join(["%{y:.2s}"]),textposition='outside')
    ],
    layout=dict(#title='2024', title_x=.45, 
                height=300, 
                barmode='group', template='plotly_dark', 
                hoverlabel=dict(font_size=18,font_family="Rockwell"),
                legend=dict(x=0.02, y=1.5, orientation='h',font_color='#5A5856'),
                bargap=0.15,bargroupgap=0.1)
)

l2_fig.update_traces(texttemplate='%{y:.3s}')
l2_fig.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=10),title_font=dict(color='#5A5856',size=25))
l2_fig.update_yaxes(showticklabels=False,showgrid=True,gridcolor="#B1A999")

# DAILY BY MARKET SEGMENT
df = all_sales[all_sales.market_segment != 'Samples'].groupby([all_sales.date,'market_segment']).usd.sum().reset_index().set_index('date')
df = round(df[df.index>'2024-03-31']).sort_values(by='market_segment',ascending=False)

# Current Month Bar Chart Constants
chart_height = 300
title = f"{df.index.max().month_name()} - ${df.usd.sum():,.0f}"
config = {'displayModeBar': False}

# CURRENT MONTH BAR BY MARKET SEGMENT
scatter_market = px.bar(
    df,
    y='usd',
    template = 'plotly_dark',
    labels={'date':'',
            'usd':''},
    height=chart_height,
    color='market_segment',
    color_discrete_map=market_segment_dict,
    title=title
)

scatter_market.for_each_trace(lambda t: t.update(name = market_legend_dict[t.name]))
scatter_market.update_coloraxes(showscale=False)
scatter_market.update_yaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=14),showticklabels=True)
scatter_market.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=10),title_font=dict(color='#5A5856',size=25))
scatter_market.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
scatter_market.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),
                              title_x=.45,
                              showlegend=True,
                              legend=dict(orientation='h',
                                          yanchor="bottom",
                                          y=1.75,
                                          xanchor="center",
                                          x=.5,
                                          title=''))

# DAILY BY SALE ORIGIN
df = all_sales[all_sales.market_segment != 'Samples'].groupby([all_sales.date,'sale_origin']).usd.sum().reset_index().set_index('date')
df = round(df[df.index>'2024-03-31'].sort_index())

scatter_origin = px.bar(
        df,
        y='usd',
        template = 'plotly_dark',
        labels={'date':'',
                'usd':''},
        height=chart_height,
        color='sale_origin',
        color_discrete_map=sale_origin_dict,
        # text_auto='.2s',
        opacity=.75,
        title=title
    )

scatter_origin.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>')
scatter_origin.update_yaxes(showgrid=True,tickprefix='$',gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=14),showticklabels=True)
scatter_origin.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=10),title_font=dict(color='#5A5856',size=25))
scatter_origin.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
scatter_origin.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),
                             showlegend=True, title_x=.45,
                              legend=dict(orientation='h',
                                          yanchor="bottom",
                                          y=1.75,
                                          xanchor="right",
                                          x=.65,
                                          title=''))

# DAILY BY All (level 2)
df = all_sales[all_sales.market_segment != 'Samples'].groupby('date').usd.sum().reset_index().set_index('date')
df = round(df[df.index>'2024-03-31'].sort_index())

bar_all = px.bar(
        df,
        y='usd',
        template = 'plotly_dark',
        labels={'date':'',
                'usd':''},
        height=chart_height,
        # text_auto='.2s',
        opacity=.8,
        title=title
    )
bar_all.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>')
bar_all.update_traces(marker_color='#E09641')
bar_all.update_yaxes(showticklabels=True,showgrid=True,tickprefix='$',gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=14))
bar_all.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=10),title_font=dict(color='#5A5856',size=15))
bar_all.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
bar_all.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),
                                                    showlegend=True, title_x=.45,
                                                    legend=dict(orientation='h',
                                                    yanchor="bottom",
                                                    y=1.75,
                                                    xanchor="right",
                                                    x=.65,
                                                    title=''))

# LEVEL 1 DAILY BAR
l1['usd'] = l1['sub_total']*.75
l1_bar_df = round(l1[l1.completed_date>'2024-03-31'].groupby('completed_date')['usd'].sum(),2).reset_index().set_index('completed_date')
title_l1 = l1_bar_df.usd.sum()

level_1_bar = px.bar(l1_bar_df,
                     y='usd',
                     template='plotly_dark',
                     labels={'usd':'',
                             'completed_date':''},
                     height=chart_height,
                     text_auto=",.2s",
                     opacity=.8,
                     title=f"April - ${l1_bar_df.usd.sum():,.0f}")

level_1_bar.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>',marker_color="#5a5856")
level_1_bar.update_coloraxes(showscale=False)
level_1_bar.update_yaxes(showticklabels=False,showgrid=True,tickprefix='$',gridcolor="#B1A999",tickvals=[0,25000,50000,75000,100000],tickfont=dict(color='#5A5856', size=14))
level_1_bar.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=11),title_font=dict(color='#5A5856',size=15))
level_1_bar.update_xaxes(tickmode='array',tickvals = l1_bar_df.index, ticktext=l1_bar_df.index.strftime('<b>%a<br>%d</b>'))
level_1_bar.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"), title_x=.45)

# l1_df = pd.DataFrame(l1[(l1.customer_type != 'Samples') & (l1.completed_date>'2024-03-31')].groupby(['completed_date','customer_name'],as_index=False)['usd'].sum())
# l1_df = round(l1_df).reset_index(drop=True).set_index('completed_date').sort_index(ascending=False)

true_df = round(all_sales[(all_sales.market_segment != 'Samples') & (all_sales.date>'2024-02-29')].drop(columns=['item','customer','qty','cad','month','year']))#.reset_index(drop=True).set_index('date')
true_df1 = true_df.groupby(['date','parent_customer'],as_index=False)['usd'].sum().reset_index(drop=True).set_index('date').sort_index(ascending=False)
true_df2 = true_df.groupby(['date','sale_origin'],as_index=False)['usd'].sum().reset_index(drop=True).set_index('date').sort_index(ascending=False)
true_df3 = true_df.groupby(['date','market_segment'],as_index=False)['usd'].sum().reset_index(drop=True).set_index('date').sort_index(ascending=False)

st.subheader("")
with st.expander("Show Current Month Detail"):
    tab0, tab1, tab2, tab3 = st.tabs(["Direct","tRUE", "tSource", "tMarket"])
    with tab0:
        st.plotly_chart(level_1_bar,config=config, use_container_width=True)
    with tab1:
        st.plotly_chart(bar_all,config=config, use_container_width=True)
    with tab2:
        st.plotly_chart(scatter_origin,config=config, use_container_width=True)
    with tab3:
        st.plotly_chart(scatter_market,config=config, use_container_width=True)

col0, col1, col2, col3= st.columns([1,2.1,2,2])
with col0:
    st.header("")
with col1:
    st.markdown(f'<h4 style="color: #5A5856">Direct<br><small>{l1_yoy_chg_perc}&nbsp yoy</small></h4>', unsafe_allow_html=True)
    st.markdown(f"<h2><b>${l1_sales_24/1000000:.2f}</b>M</h2>", unsafe_allow_html=True)
with col2:
    st.markdown("")
    st.image(r"assets/Nevil.png",width=65)
    st.markdown(f"<h5>&nbsp&nbsp&nbsp&nbsp2024</h5>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<h4 style='color: #E09641; outline-color: #E09641;'>tRUE<br><small>+{yoy_chg_perc}&nbsp yoy</small></h4>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color: #E09641; outline-color: #E09641;'><b>${sales_24/1000000:.2f}M</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(['Direct', 'TRUE'])
with tab1:
    st.plotly_chart(l1_fig,config=config, use_container_width=True)
with tab2:
    st.plotly_chart(l2_fig, config=config, use_container_width=True)

# market segment rolling-52's
df = all_sales[(all_sales.market_segment!='Samples') & (all_sales.market_segment!='Other')].set_index('date').groupby([pd.Grouper(freq='SM'),'market_segment'])['usd'].sum().reset_index().set_index('date')
df = df[df.index>'2023-04-30'].pivot(columns='market_segment', values='usd')

area_market = px.area(df,
              color='market_segment',
              color_discrete_map=market_segment_dict, 
              facet_col="market_segment",facet_col_wrap=2, facet_col_spacing=.1, facet_row_spacing=.15,
              height=650,
              template = 'plotly_dark',
              labels={'value':"",'market_segment':""}
             )

area_market.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>',fill='tonexty')
area_market.update_yaxes(showticklabels=True,showgrid=True,gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=14),matches=None)
area_market.update_xaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
area_market.update_xaxes(showticklabels=True, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
area_market.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),legend=dict(x=0, y=1.2, orientation='h',title=None),showlegend=False)
area_market.for_each_annotation(lambda a: a.update(text=a.text.replace("=", "")))

# MARKET SEGMENT BOXES
def calculate_yearly_sales_difference(all_sales, year, market_segment, year_ago_date):
    """Calculate the difference in yearly sales and percentage change for a specific market segment."""
    current_year_sales = all_sales[(all_sales['date'].dt.year == year) & (all_sales['market_segment'] == market_segment)].usd.sum()
    previous_year_sales = all_sales[
        (all_sales['date'].dt.year == year - 1) & 
        (all_sales['market_segment'] == market_segment) & 
        (all_sales['date'].dt.date < year_ago_date.date())
    ].usd.sum()
    
    yoy_sales_difference = int(current_year_sales - previous_year_sales)
    if previous_year_sales != 0:
        yoy_sales_percentage = round(yoy_sales_difference / previous_year_sales, 2)
    else:
        yoy_sales_percentage = 0
    
    return yoy_sales_difference, yoy_sales_percentage

market_segments = [
    'Vending', 'Online', 'Alternate Retail', 'Convenience', 
    'Canada', 'Grocery', 'Broadline Distributor', 'Other'
]

# Calculate yearly sales difference and percentage change for each market segment
yoy_data = {}
for segment in market_segments:
    yoy_difference, yoy_percentage = calculate_yearly_sales_difference(all_sales, 2024, segment, year_ago_today)
    yoy_data[segment] = {'difference': yoy_difference, 'percentage': yoy_percentage}

col1, col2, col3, col4 = st.columns(4)

for i, segment in enumerate(market_segments):
    yoy_difference, yoy_percentage = calculate_yearly_sales_difference(all_sales, 2024, segment, year_ago_today)
    value = f"${millify(all_sales[(all_sales['date'].dt.year == 2024) & (all_sales['market_segment'] == segment)].usd.sum())}"
    
    # Display metrics for the current market segment
    if i < 2:
        col = col1
    elif i < 4:
        col = col2
    elif i < 6:
        col = col3
    else:
        col = col4
    
    col.metric(
        label=segment, 
        value=value, 
        delta=f"{yoy_percentage:.0%}"
    )

with st.expander("Show 52-Week Market Segment Trends"):
    st.plotly_chart(area_market,config=config, use_container_width=True)