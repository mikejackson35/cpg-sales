import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sqlalchemy import create_engine
import numpy as np
from datetime import datetime
from millify import millify
import plotly.graph_objects as go
from main_utils import market_segment_dict, sale_origin_dict, market_legend_dict


st.set_page_config(page_title='Sales Dashboard',
                   page_icon='assets/your-logo-here-placeholder.jpg',
                   layout='wide'
)
config = {'displayModeBar': False}

alt.themes.enable("dark")

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
config = {'displayModeBar': False}

# GET DATA
###############
# DIRECT
@st.cache_data
def get_direct():
    direct_sales = pd.read_csv(r"data/direct_sales.csv", encoding='utf-8')
    direct_sales = direct_sales[direct_sales.status=='Closed']
    return direct_sales
direct_sales = get_direct()

# TRUE
@st.cache_data
def get_true():
    true_sales = pd.read_csv(r"data/true_sales.csv", encoding='utf-8')
    true_sales = true_sales[true_sales.status=='Closed']
    return true_sales
true_sales = get_true()

# UPDATE TIMESTAMP
direct_sales.date = pd.to_datetime(direct_sales.date, errors='coerce')
true_sales.date = pd.to_datetime(true_sales.date, errors='coerce')


# FILTERS
week_ago = datetime.today().date() - pd.offsets.Day(10)
recent_sales = direct_sales[direct_sales.date>week_ago]
current_date = datetime.today().strftime('%Y-%m-%d')
import datetime
year_ago_today = datetime.datetime.today() - datetime.timedelta(days=365)


# SALES SUMMARY
direct_sales_24 = int(direct_sales[(direct_sales['date'] > '2023-12-31') & (direct_sales['date'] < current_date)].amount.sum())
direct_sales_23 = int(direct_sales[(direct_sales['date'] > '2022-12-31') & (direct_sales['date'].dt.date < year_ago_today.date())].amount.sum())
direct_yoy_chg_perc = f"{(direct_sales_24/direct_sales_23-1)*100:.0f}%"

true_sales_24 = int(true_sales[(true_sales['date'] > '2023-12-31') & (true_sales['date'] < current_date)].amount.sum())
true_sales_23 = int(true_sales[(true_sales['date'] > '2022-12-31') & (true_sales['date'].dt.date < year_ago_today.date())].amount.sum())
yoy_chg_perc = f"{(true_sales_24/true_sales_23-1)*100:.0f}%"


###################
# direct_sales Main Bar
dir_main_bar = direct_sales[['date','amount']].sort_values(by='date',ascending=False)
dir_main_bar['year'] = dir_main_bar['date'].dt.year
dir_main_bar['YearMonth'] = dir_main_bar['date'].astype('string').apply(lambda x: x.split("-")[0] + "-" + x.split("-")[1])

dir_main_bar = dir_main_bar.groupby(['year','YearMonth'],as_index=False)['amount'].sum()

dir_23 = dir_main_bar[dir_main_bar.year==2023].amount
dir_24 = dir_main_bar[dir_main_bar.year==2024].amount
goal = dir_23 * 2

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

color = dir_main_bar.year.astype('category').unique()
bar_height = 400

dir_fig = go.Figure(
    data=[
        go.Bar(
            x=months, 
            y=dir_23, 
            name="2023", 
            marker_color="#909497",
            textfont=dict(color='#909497', size=16, family='Arial Black'),  # Adjust size and family as needed
            marker_line_color="#909497", 
            marker_opacity=.5,
            hovertemplate="<br>".join(["%{y:.2s}"]),
            textposition='outside'
        ),
        go.Bar(
            x=months, 
            y=dir_24, 
            name="2024", 
            marker_color='#FFFFFF',
            textfont=dict(color='white', size=22, family='Arial Black'),  # Adjust size and family as needed
            marker_line_color="#5A5856",
            hovertemplate="<br>".join(["%{y:.2s}"]),
            textposition='outside'
        )
    ],
    layout=dict(
        height=bar_height, 
        barmode='group', 
        template='plotly_dark', 
        hoverlabel=dict(font_size=18, font_family="Rockwell"),
        legend=dict(x=0.02, y=1.5, orientation='h', font_color='#5A5856'),
        bargap=0.15, 
        bargroupgap=0.1
    )
)

dir_fig.update_traces(texttemplate='%{y:.3s}')
dir_fig.update_xaxes(showgrid=False, gridcolor='gray', tickfont=dict(color='#5A5856', size=15), title_font=dict(color='#5A5856', size=25))
dir_fig.update_yaxes(showticklabels=False, showgrid=True, gridcolor="lightgrey")
dir_fig.update_yaxes(range=[0, max(max(dir_23), max(dir_24)) * 1.2])



###################
# L2 Main Bar

true_sales['year'] = true_sales['date'].dt.year
true_sales['month'] = true_sales['date'].dt.month_name()
true_sales['YearMonth'] = true_sales['date'].astype('string').apply(lambda x: x.split("-")[0] + "-" + x.split("-")[1])

# group by month year and add $0 sales to future months
chart_df = round(true_sales.groupby(['year','YearMonth'],as_index=False)['amount'].sum())

true_23 = chart_df[chart_df.year==2023].amount
true_24 = chart_df[chart_df.year==2024].amount

goal = true_23 * 2

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

color = chart_df.year.astype('category').unique()

######
true_fig = go.Figure(
    data=[
        go.Bar(
            x=months, 
            y=true_23, 
            name="2023", 
            marker_color="#909497",
            textfont=dict(color='#909497', size=16, family='Arial Black'),  # Consistent font style
            marker_line_color="#909497", 
            marker_opacity=.5,
            hovertemplate="<br>".join(["%{y:.2s}"]),
            textposition='outside'
        ),
        go.Bar(
            x=months, 
            y=true_24, 
            name="2024", 
            marker_color= '#000000',
            textfont=dict(color='black', size=16, family='Arial Black'),  # Consistent font style
            marker_line_color= '#000000',
            hovertemplate="<br>".join(["%{y:.2s}"]),
            textposition='outside'
        )
    ],
    layout=dict(
        height=bar_height, 
        barmode='group', 
        template='plotly_dark', 
        hoverlabel=dict(font_size=18, font_family="Rockwell"),
        legend=dict(x=0.02, y=1.5, orientation='h', font_color='#5A5856'),
        bargap=0.15, 
        bargroupgap=0.1
    )
)

true_fig.update_traces(texttemplate='%{y:.3s}')
true_fig.update_xaxes(
    showgrid=False, 
    gridcolor='gray', 
    tickfont=dict(color='#5A5856', size=15), 
    title_font=dict(color='#5A5856', size=25)
)
true_fig.update_yaxes(
    showticklabels=False, 
    showgrid=True, 
    gridcolor="lightgrey",
    range=[0, max(max(true_23), max(true_24)) * 1.2]  # Adjust range to reflect true_23 and true_24 values
)

######


# DAILY BY MARKET SEGMENT
df = true_sales[(true_sales.date>'2024-10-31') & (true_sales.date<'2024-11-30')].groupby([true_sales.date,'cust_segment']).amount.sum().reset_index().set_index('date')
df = round(df[(df.index>'2024-10-31') & (df.index<'2024-11-30')].sort_index())

# Current Month Bar Chart Constants
chart_height = 300
title = f"{df.index.max().month_name()} - ${df.amount.sum():,.0f}"
config = {'displayModeBar': False}

# CURRENT MONTH DAILY BAR BY MARKET SEGMENT
bar_market = px.bar(
    df,
    y='amount',
    template = 'plotly_dark',
    labels={'date':'',
            'amount':''},
    height=chart_height,
    color='cust_segment',
    color_discrete_map=market_segment_dict,
    title=title
)

# bar_market.for_each_trace(lambda t: t.update(name = market_legend_dict[t.name]))
bar_market.update_coloraxes(showscale=False)
bar_market.update_yaxes(showgrid=True,tickprefix='$',gridcolor="lightgrey",tickfont=dict(color='#5A5856', size=14),showticklabels=True)
bar_market.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=10),title_font=dict(color='#5A5856',size=25))
bar_market.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
bar_market.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),
                              title_x=.45,
                              showlegend=True,
                              legend=dict(orientation='h',
                                          yanchor="bottom",
                                          y=1.75,
                                          xanchor="center",
                                          x=.5,
                                          title=''))

# CURRENT MONTH DAILY BAR BY SALE ORIGIN
df = true_sales.groupby([true_sales.date,'source']).amount.sum().reset_index().set_index('date')
df = round(df[(df.index>'2024-10-31') & (df.index<'2024-11-30')].sort_index())

bar_origin = px.bar(
        df,
        y='amount',
        template = 'plotly_dark',
        labels={'date':'',
                'amount':''},
        height=chart_height,
        color='source',
        color_discrete_map=sale_origin_dict,
        # text_auto='.2s',
        opacity=.75,
        title=title
    )

bar_origin.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>')
bar_origin.update_yaxes(showgrid=True,tickprefix='$',gridcolor="lightgrey",tickfont=dict(color='#5A5856', size=14),showticklabels=True)
bar_origin.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=10),title_font=dict(color='#5A5856',size=25))
bar_origin.update_xaxes(tickmode='array',tickvals = df.index, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
bar_origin.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),
                             showlegend=True, title_x=.45,
                              legend=dict(orientation='h',
                                          yanchor="bottom",
                                          y=1.75,
                                          xanchor="right",
                                          x=.65,
                                          title=''))

# CURRENT MONTH DAILY TRUE BAR - ALL
df = true_sales.groupby('date').amount.sum().reset_index().set_index('date')
df = round(df[(df.index>'2024-10-31') & (df.index<'2024-11-30')].sort_index())

bar_all = px.bar(
        df,
        y='amount',
        template = 'plotly_dark',
        labels={'date':'',
                'amount':''},
        height=chart_height,
        text_auto='.2s',
        opacity=.8,
        title=title
    )
bar_all.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>')
bar_all.update_traces(marker_color= '#000000')
bar_all.update_yaxes(showticklabels=True,showgrid=True,tickprefix='$',gridcolor="lightgrey",tickfont=dict(color='#5A5856', size=14))
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

# CURRENT MONTH DAILY BAR DIRECT
# direct_sales['amount'] = direct_sales['amount']*.75
direct_sales_bar_df = round(direct_sales[(direct_sales.date>'2024-10-31') & (direct_sales.date<'2024-11-30')].groupby('date')['amount'].sum(),2).reset_index().set_index('date')
title_direct_sales = direct_sales_bar_df.amount.sum()

direct_bar = px.bar(direct_sales_bar_df,
                     y='amount',
                     template='plotly_dark',
                     labels={'amount':'',
                             'completed_date':''},
                     height=chart_height,
                     text_auto=",.2s",
                     opacity=.8,
                     title=f"November - ${direct_sales_bar_df.amount.sum():,.0f}")

direct_bar.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>',marker_color="#FFFFFF")
direct_bar.update_coloraxes(showscale=False)
direct_bar.update_yaxes(showticklabels=False,showgrid=True,tickprefix='$',gridcolor="lightgrey",tickvals=[0,25000,50000,75000,100000],tickfont=dict(color='#5A5856', size=14))
direct_bar.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=11),title_font=dict(color='#5A5856',size=15))
direct_bar.update_xaxes(tickmode='array',tickvals = direct_sales_bar_df.index, ticktext=direct_sales_bar_df.index.strftime('<b>%a<br>%d</b>'))
direct_bar.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"), title_x=.45)

# direct_sales_df = pd.DataFrame(direct_sales[(direct_sales.customer_type != 'Samples') & (direct_sales.completed_date>'2024-03-31')].groupby(['completed_date','customer_name'],as_index=False)['amount'].sum())
# direct_sales_df = round(direct_sales_df).reset_index(drop=True).set_index('completed_date').sort_index(ascending=False)

true_df = round(true_sales.drop(columns=['cust_name']))#.reset_index(drop=True).set_index('date')
true_df1 = true_df.groupby(['date','cust_parent_name'],as_index=False)['amount'].sum().reset_index(drop=True).set_index('date').sort_index(ascending=False)
true_df2 = true_df.groupby(['date','source'],as_index=False)['amount'].sum().reset_index(drop=True).set_index('date').sort_index(ascending=False)
true_df3 = true_df.groupby(['date','cust_segment'],as_index=False)['amount'].sum().reset_index(drop=True).set_index('date').sort_index(ascending=False)

# market segment area chart rolling-52's
df = true_sales[true_sales.cust_segment!='No Segment'].set_index('date').groupby([pd.Grouper(freq='SM'),'cust_segment'])['amount'].sum().reset_index().set_index('date')
df = df[df.index>'2023-12-31'].pivot(columns='cust_segment', values='amount')

area_market = px.area(df,
            color='cust_segment',
            color_discrete_map=market_segment_dict, 
            facet_row="cust_segment",#facet_col_wrap=2, facet_col_spacing=.1, facet_row_spacing=.11,
            height=2000,
            template = 'plotly_dark',
            labels={'date':"",'cust_segment':""}
            )

area_market.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m-%d}<br>',fill='tonexty')
area_market.update_yaxes(showticklabels=True,showgrid=True,gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=14),matches=None)
area_market.update_xaxes(tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
area_market.update_xaxes(showticklabels=True, ticktext=df.index.strftime('<b>%a<br>%d</b>'))
area_market.update_layout(hoverlabel=dict(font_size=18,font_family="Rockwell"),legend=dict(x=0, y=1.2, orientation='h',title=None),showlegend=False)
area_market.for_each_annotation(lambda a: a.update(text=a.text.replace("=", "")))

main_col_1, space, main_col_2 = st.columns([2.25,.25,1.5])

with main_col_1:
    st.subheader("")
    with st.expander("Show Current Month Detail"):
        tab0, tab1, tab2, tab3 = st.tabs(["Direct","True", "tSource", "tMarket"])
        with tab0:
            st.plotly_chart(direct_bar,config=config, use_container_width=True)
        with tab1:
            st.plotly_chart(bar_all,config=config, use_container_width=True)
        with tab2:
            st.plotly_chart(bar_origin,config=config, use_container_width=True)
        with tab3:
            st.plotly_chart(bar_market,config=config, use_container_width=True)

    st.write("#")        
    col0, col1, col2, col3= st.columns([1,2.1,2,2])
    with col0:
        st.header("")
    with col1:
        st.markdown(f'<h4 style="color: #FFFFFF">Direct<br><small>+{direct_yoy_chg_perc}&nbsp yoy</small></h4>', unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: #FFFFFF'><b>${direct_sales_24/1000000:.2f}</b>M</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown("")
        # st.image(r'assets/logo_wilde_chips.jpg', width=100)
        st.markdown(f"<h5>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp2024</h5>", unsafe_allow_html=True)
        st.markdown(f"<small>thru: {true_sales.date.max().strftime('%a %b %d')}", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<h4 style='color: #000000; outline-color: #000000;'>True<br><small>+{yoy_chg_perc}&nbsp yoy</small></h4>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: #000000; outline-color: #000000;'><b>${true_sales_24/1000000:.2f}M</h2>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(['Direct', 'TRUE'])
    with tab1:
        st.plotly_chart(dir_fig,config=config, use_container_width=True)
    with tab2:
        st.plotly_chart(true_fig, config=config, use_container_width=True)

with main_col_2:
    st.subheader("")
    with st.expander("Show 52-Week Market Segment Trends"):
        st.plotly_chart(area_market,config=config, use_container_width=True)

    # MARKET SEGMENT BOXES
    def calculate_yearly_sales_difference(true_sales, year, cust_segment, year_ago_date):
        """Calculate the difference in yearly sales and percentage change for a specific market segment."""
        current_year_sales = true_sales[(true_sales['date'].dt.year == year) & (true_sales['cust_segment'] == cust_segment)].amount.sum()
        previous_year_sales = true_sales[
            (true_sales['date'].dt.year == year - 1) & 
            (true_sales['cust_segment'] == cust_segment) & 
            (true_sales['date'].dt.date < year_ago_date.date())
        ].amount.sum()
        
        yoy_sales_difference = int(current_year_sales - previous_year_sales)
        if previous_year_sales != 0:
            yoy_sales_percentage = round(yoy_sales_difference / previous_year_sales, 2)
        else:
            yoy_sales_percentage = 0

        return yoy_sales_difference, yoy_sales_percentage

    # Calculate yearly sales difference and percentage change for each market segment
    market_segments = list(true_sales[(true_sales.cust_segment != 'Export') & (true_sales.cust_segment != 'No Segment')]
                        .groupby('cust_segment').amount.sum().sort_values(ascending=False).index)

    yoy_data = {}
    for segment in market_segments:
        yoy_difference, yoy_percentage = calculate_yearly_sales_difference(true_sales, 2024, segment, year_ago_today)
        yoy_data[segment] = {'difference': yoy_difference, 'percentage': yoy_percentage}

    col1, col2 = st.columns(2)

    for i, segment in enumerate(market_segments):
        yoy_difference, yoy_percentage = calculate_yearly_sales_difference(true_sales, 2024, segment, year_ago_today)
        value = f"${millify(true_sales[(true_sales['date'].dt.year == 2024) & (true_sales['cust_segment'] == segment)].amount.sum(), precision=1)}"
        
        # Display metrics for the current market segment
        if i < 6:
            col = col1
        else:
            col = col2
        
        col.metric(
            label=segment, 
            value=value, 
            delta=f"{yoy_percentage:.0%}",
        )

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)