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

st.set_page_config(page_title='Charts',
                   page_icon=":bar_chart:",
                   layout='centered'
)

alt.themes.enable("dark")

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)



# TRUE
# @st.cache_data
# def get_true():
true_sales = pd.read_csv(r"data/true_sales.csv", encoding='utf-8',low_memory=False)
true_sales = true_sales[true_sales.status=='Closed']
#     return true_sales
# true_sales = get_true()


# invoice date cleanup
true_sales['date'] = pd.to_datetime(true_sales['date'])
true_sales['date'] = true_sales['date'].dt.normalize()
true_sales['date'] = true_sales['date'].dt.floor('D')

unique_cust_parent_names = list(true_sales.cust_parent_name.unique())
unique_cust_parent_names_sorted = sorted(filter(None, unique_cust_parent_names))

unique_cust_segments = list(true_sales.cust_segment.unique())
unique_cust_segments_sorted = sorted(filter(None, unique_cust_segments))

# --- FILTERS AND SIDEBAR ----
year = st.sidebar.multiselect(
    label = 'Year',
    options=np.array(true_sales['date'].dt.year.unique()),
    default=np.array(true_sales['date'].dt.year.unique()[1:]),
)
source = st.sidebar.multiselect(
    label = 'Direct or Dot',
    options=np.array(true_sales['source'].unique()),
    default=np.array(true_sales['source'].unique()),
)
segment = st.sidebar.multiselect(
    label='Market Segment',
    options=unique_cust_segments_sorted,
    default=unique_cust_segments_sorted
)

parent = st.sidebar.multiselect(
    label='Parent cust_name',
    options=unique_cust_parent_names_sorted,
    default=unique_cust_parent_names_sorted,
)

# COLOR DICTIONARIES
market_segment_dict = {
    'Natural': 'rgb(56,149,73)',
    'Grocery': 'rgb(248,184,230)',
    'Specialty Retail': 'rgb(46,70,166)',
    'Club': 'rgb(46,70,166)',
    'Mass': 'rgb(204,208,221)',
    'Online': 'rgb(106,87,63)',
    'Off-Shore / Military': 'rgb(200,237,233)',
    'Convenience': 'rgb(233,81,46)',
    'Broadline': 'rgb(233,152,19)',
    'Drug': 'rgb(141,62,92)',
    'Outlet': 'rgb(200,237,233)',
    'Fitness': 'rgb(233,81,46)',
    'Export': 'rgb(233,152,19)',
    'No Segment': 'rgb(141,62,92)'
    }

# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = true_sales[
    (true_sales['date'].dt.year.isin(year)) &
    (true_sales['cust_segment'].isin(segment)) &
    (true_sales['source'].isin(source)) &
    (true_sales['cust_parent_name'].isin(parent))
    ]

start = df_selection.date.min().date()
end = df_selection.date.max().date()

cust_name_count = int(df_selection.cust_name.nunique())
sales = int(df_selection.amount.sum())
# mean_sales = int(sales/cust_name_count)


config = {'displayModeBar': False}
df_selection = df_selection.sort_values(by='amount',ascending=True)
seg_sales = round(df_selection.groupby('cust_segment',as_index=False)['amount'].sum()).sort_values(by='amount',ascending=True)

fig_seg_sales = px.pie(
    seg_sales, 
    values='amount', 
    names='cust_segment',
    template = 'plotly_dark',
    title=' ',
    opacity = .8,
    hole=.33,
    hover_name='cust_segment',
    color='cust_segment',
    color_discrete_map=market_segment_dict).update_layout(showlegend=False, autosize=True, width=450,height=450)

fig_seg_sales.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}<br>%{percent:.0%}',hovertemplate = '%{label}<br>%{value:.2s}')

## monthly bar chart
df_selection.index = pd.to_datetime(df_selection['date'])
mth_sales = round(df_selection.groupby(pd.Grouper(freq='M'))[['amount']].sum())

fig_mth_bar = px.bar(mth_sales.reset_index(),
        template='plotly_dark',
        x= 'date',
        y='amount',
        labels = {'date':' ','amount':''},
        text='amount',
        opacity=.8,
        height=260,
        ).update_coloraxes(showscale=False)
fig_mth_bar.update_traces(marker_color='#000000',texttemplate='%{text:$,.2s}',hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')
fig_mth_bar.update_xaxes(showgrid=False,gridcolor='gray',tickvals = mth_sales.index,ticktext=mth_sales.index.strftime('%b-%y'),tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
fig_mth_bar.update_yaxes(showgrid=False,tick0=0,dtick=250000,showticklabels=False, tickcolor='darkgrey', gridcolor='darkgrey')   

# WEEKLY SCATTER CHART
df_selection.index = pd.to_datetime(df_selection['date'])
sales_per_week = df_selection.groupby(pd.Grouper(freq='W'))['amount'].sum()

fig_scatter_all = px.scatter(
    round(sales_per_week),
    x=sales_per_week.index,
    y='amount',
    # title='10-Wk Moving Avg',
    # template = 'plotly_dark',
    labels={'date':'',
            'amount':''},
    height=260,
    color='amount',
    color_continuous_scale=px.colors.sequential.Oranges,
    trendline="rolling", trendline_options=dict(function="mean", window=10), trendline_scope="overall", trendline_color_override="grey"
)
fig_scatter_all.update_traces(name="",hovertemplate="Sales: <b>%{y:$,.0f}")
fig_scatter_all.update_traces(marker=dict(size=8,color='#000000',opacity=.9,line=dict(width=1,color='lightgrey')),selector=dict(mode='markers'))
fig_scatter_all.update_coloraxes(showscale=False)
fig_scatter_all.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_scatter_all.update_layout(hovermode='x unified',showlegend=False,legend_title_text='')#,title_x=.4,legend=dict(y=0.99, x=0.1,title='10-Wk Moving Avg'),legend_title_text='')
fig_scatter_all.update_layout(hoverlabel=dict(font_size=15,font_family="Rockwell"))
fig_scatter_all.update_xaxes(showticklabels=True,showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=14),title_font=dict(color='#5A5856',size=15))
# fig_scatter_all.update_yaxes(tick0=0,dtick=250000)

###################
# tRUE YoY by Month Sales

true_sales['year'] = true_sales['date'].dt.year
true_sales['month'] = true_sales['date'].dt.month_name()
true_sales['YearMonth'] = true_sales['date'].astype('string').apply(lambda x: x.split("-")[0] + "-" + x.split("-")[1])

# group by month year and add $0 sales to future months
chart_df = round(true_sales[(true_sales['source'].isin(source) &
                            true_sales['cust_segment'].isin(segment) &
                            true_sales['cust_parent_name'].isin(parent))]
                            .groupby(['year','YearMonth'],as_index=False)['amount'].sum()
                            )

sales_23_ = chart_df[(chart_df.year==2023)].amount
sales_24_ = chart_df[chart_df.year==2024].amount

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

color = chart_df.year.astype('category').unique()

# Bar and scatter monthly
l2_fig = go.Figure(
    data=[
        go.Bar(x=months, y=sales_23_, name="2023", marker_color="#909497",textfont=dict(color='#D6D8CF'), marker_line_color="#909497", marker_opacity=.5,hovertemplate="<br>".join(["%{y:.2s}"])),#,textposition='outside'),
        go.Bar(x=months, y=sales_24_, name="2024", marker_color='#000000',textfont=dict(color='white',size=25), marker_line_color="#E09641",hovertemplate="<br>".join(["%{y:.2s}"])),#,textposition='outside')
    ],
    layout=dict(#title='2024', title_x=.45, 
                height=260, 
                barmode='group', template='plotly_dark', 
                hoverlabel=dict(font_size=18,font_family="Rockwell"),
                legend=dict(x=0.02, y=1.5, orientation='h',font_color='#5A5856'),
                bargap=0.15,bargroupgap=0.1)
)

l2_fig.update_traces(texttemplate='$%{y:.3s}')
l2_fig.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=25))
l2_fig.update_yaxes(showticklabels=False,showgrid=False,gridcolor="#B1A999",tickfont=dict(color='#5A5856', size=13))

# distributor bar chart
top_custs = pd.DataFrame(df_selection.groupby(['cust_name','cust_segment'],as_index=False)['amount'].sum().sort_values(by='amount',ascending=False)[:25])
fig_dist_sales = px.bar(top_custs,
       x = 'cust_name',
       y = 'amount',
    template = 'plotly_dark',
    labels={'cust_name':'',
            'amount':' '},
    opacity=.8,
    height=400,
    # width=1000,        
    color = 'cust_segment',
    text = 'amount',
    color_discrete_map=market_segment_dict).update_layout(showlegend=False)

fig_dist_sales.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_dist_sales.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=11),title_font=dict(color='#5A5856',size=15))#,tickangle=30)
fig_dist_sales.update_traces(texttemplate='%{text:$,.2s}',hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')#,textposition='outside')


# parent distributor bar
top_parents = pd.DataFrame(df_selection.groupby(['cust_parent_name','cust_segment'],as_index=False)['amount'].sum().sort_values(by='amount',ascending=False)[:15])
fig_parent_sales = px.bar(top_parents,
                          x = 'cust_parent_name',
                          y = 'amount',
                          template = 'plotly_dark',
                          labels={'cust_parent_name':'',
                                'amount':''},
                          height=350,
                          opacity = .8,
                          color = 'cust_segment',
                          text = 'amount',
                          color_discrete_map=market_segment_dict).update_layout(showlegend=False)

fig_parent_sales.update_traces(hovertemplate = '$%{y:.2s}'+'<br>%{x:%Y-%m}<br>')
fig_parent_sales.update_yaxes(showgrid=True,showticklabels=True,gridcolor='darkgray',tickfont=dict(color='#5A5856', size=13),automargin=True) 
fig_parent_sales.update_xaxes(showgrid=False,gridcolor='gray',tickfont=dict(color='#5A5856', size=13),title_font=dict(color='#5A5856',size=15))
fig_parent_sales.update_traces(texttemplate='%{text:$,.2s}')

col1, col2 = st.columns(2)
with col1:
    st.markdown("###")
    st.markdown("###")
    st.markdown("###")
    st.markdown("###")
    st.header("True Sales")
    st.markdown(f"<h4><b>${millify(df_selection.amount.sum(),precision=2)}</b><br><br><b>{start}</b> <br><small>thru</small><br><b>{end}</b>",unsafe_allow_html=True)
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

tab1, tab2 = st.tabs(["by Parent Customer", "by Customer"])
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