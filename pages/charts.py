import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_toggle import toggle


st.set_page_config(page_title='Charts',
                   page_icon=":bar_chart:",
                   layout='wide'
)

# alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 2rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
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

# Remove whitespace from the top of the page and sidebar
# st.markdown("""
#         <style>
#                .block-container {
#                     padding-top: 1rem;
#                     padding-bottom: 0rem;
#                     padding-left: 1rem;
#                     padding-right: 1rem;
#                 }
#         </style>
#         """, unsafe_allow_html=True)

# ---- PULL IN DATA ----
# @st.cache_data
def get_data_from_csv():
    df = pd.read_csv('data/all_sales_data.csv')
    return df
df = get_data_from_csv()

### MASTER DATA ###
all_sales = df.copy()

# invoice date cleanup
all_sales['Invoice Date'] = pd.to_datetime(all_sales['Invoice Date'])
all_sales['Invoice Date'] = all_sales['Invoice Date'].dt.normalize()
all_sales['Invoice Date'] = all_sales['Invoice Date'].dt.floor('D')
all_sales.sort_values(by='Dollars',ascending=False,inplace=True)

# --- FILTERS AND SIDEBAR ----
segment = st.sidebar.multiselect(
    "",
    options=all_sales['Market Segment'].unique(),
    default=all_sales['Market Segment'].unique(),
)

# line divider
st.markdown(" ")

# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = all_sales[
    # (all_sales['Parent Customer'].isin(parent)) &
    (all_sales['Market Segment'].isin(segment))
    ]

# theme used for charts
template = 'presentation'

# ---- TOP KPI's Row ----
sales_23 = int(df_selection[df_selection["Invoice Date"].dt.year == 2023].Dollars.sum())
sales_22 = df_selection[df_selection['Invoice Date'].dt.year == 2022]['Dollars'].sum().round(2)

def plus_minus(delta):
    if delta > 0:
        symbol = "+"
    else:
        symbol = ""
    return symbol

delta = sales_23 - sales_22
yoy_chg_perc = plus_minus(delta) + f"{int(sales_23/sales_22*100-100)}%"
customer_count = int(df_selection[df_selection["Invoice Date"].dt.year == 2023].Customer.nunique())
sales_per_customer = int(sales_23 / customer_count)


# SIDEBAR
logo, col1, col2, col3, col4 = st.columns([1,1.2,1.2,1.2,1.2])
with logo:
    st.image("assets/Nevil.png",width=150)
with col1:
    st.markdown('<h4>YTD Sales</h4>', unsafe_allow_html=True)
    st.title(f"${sales_23:,}")
with col2:
    st.markdown('<h4>YoY Change</h4>', unsafe_allow_html=True)
    st.title(f"{yoy_chg_perc}")
with col3:
    st.markdown('<h4>Num of Customers</h4>', unsafe_allow_html=True)
    st.title(F"{customer_count:,}")
with col4:
    st.markdown('<h4>$/Customer</h4>', unsafe_allow_html=True)
    st.title(f"${sales_per_customer:,}")

# line divider
st.markdown("---")

df_selection.index = pd.to_datetime(df_selection['Invoice Date'],format = '%m/%d/%y %I:%M%p')
mth_sales = df_selection.groupby(pd.Grouper(freq='M'))[['Dollars','Dollars Formatted']].sum()
mth_sales['Dollars'] = mth_sales['Dollars'].astype('int')

# need to create toggle that adds 2022 sales to bar chart
fig_mth_bar = px.bar(mth_sales[mth_sales.index.year==2023],
       template='presentation',
       x= mth_sales[mth_sales.index.year==2023].index.month,
       y='Dollars',
       color='Dollars',
       color_continuous_scale=px.colors.sequential.Oranges,
       labels = {'Invoice Date':' ','Dollars':'<b>$USD</b>'},
       text="Dollars",
       opacity=.8,
       hover_data=['Dollars'],
       title='<b>2023</b>').update_coloraxes(showscale=False)
fig_mth_bar.update_traces(texttemplate='<b>%{text:$,}</b>',hovertext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
fig_mth_bar.update_layout(title_x=0.5,hovermode="x")
fig_mth_bar.update_xaxes(tickmode='array',tickvals = [1,2,3,4,5,6,7,8,9,10,11,12], ticktext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
fig_mth_bar.update_yaxes(tick0=0,dtick=250000,showticklabels=False)

seg_sales = df_selection[df_selection["Invoice Date"].dt.year == 2023].groupby('Market Segment',as_index=False)['Dollars'].sum().sort_values(by='Market Segment',ascending=False)
fig_seg_sales = px.pie(
    seg_sales, 
    values='Dollars', 
    names='Market Segment',
    template = 'simple_white',
    title=' ',
    opacity = .8,
    hole=.4,
    hover_data = ['Market Segment']).update_layout(autosize=False,width=450,height=450,showlegend=False)
fig_seg_sales.update_traces(textposition='inside', textinfo='percent+label')

# ---- CREATE TWO COLUMNS AND PLACE GRAPHS ----
blank, left_column, right_column = st.columns([.05,2.6,1.2])
blank.markdown("##")
left_column.plotly_chart(fig_mth_bar,  theme = 'streamlit',legend=None, use_container_width=True)
right_column.plotly_chart(fig_seg_sales, theme = 'streamlit', use_container_width=True)


# line divider
st.markdown("---")

# WEEKLY SCATTER CHARTS
sales_per_day = df_selection.groupby(pd.Grouper(freq='W', key='Invoice Date'))['Dollars'].sum()
sales_per_day_2023 = sales_per_day[sales_per_day.index.year==2023]

#all sales weekly scatter
fig_scatter_all = px.scatter(
    sales_per_day,
    x=sales_per_day.index,
    y='Dollars',
    title='<b>Weekly Sales</b>',
    template = template,
    labels={'Invoice Date':'',
            'Dollars':'<b>$USD</b>'},
    height=425,
    size='Dollars',
    size_max=15,
    trendline="rolling", trendline_options=dict(function="mean", window=10), trendline_scope="overall", trendline_color_override="black"
).update_layout(title_x=0.4,hovermode="x unified")

fig_scatter_all.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        title = '10 Week Moving Average'
    )
)

#2023 weekly scatter
fig_scatter_2023 = px.scatter(
    sales_per_day_2023,
    x=sales_per_day_2023.index,
    y='Dollars',
    title='<b>Weekly Sales</b>',
    template = template,
    labels={'Invoice Date':'',
            'Dollars':'<b>$USD</b>'},
    height=425,
    size='Dollars',
    size_max=15,
    trendline="rolling", trendline_options=dict(function="mean", window=10), trendline_scope="overall", trendline_color_override="black"
).update_layout(title_x=0.4,hovermode="x unified")

fig_scatter_2023.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        title = '10 Week Moving Average'
    )
)
st.markdown("##")
# SCATTER CHART DISPLAY AND BUTTONS
st.button("2023 Only", type="primary")
if st.button('2022/2023'):
    blank_left, chart, blank_right,  = st.columns([.5,2.8,.5])
    blank_left.markdown("##")
    chart.plotly_chart(fig_scatter_all, theme = 'streamlit', use_container_width=True)
    blank_right.markdown("##")
else:
    blank_left, chart, blank_right,  = st.columns([.5,2.8,.5])
    blank_left.markdown("##")
    chart.plotly_chart(fig_scatter_2023, theme = 'streamlit', use_container_width=True)
    blank_right.markdown("##")

# ---- CREATE ROW 2 MORE GRAPHS ----

# distributor bar
top_custs = pd.DataFrame(df_selection[df_selection["Invoice Date"].dt.year == 2023].groupby(['Customer','Market Segment'],as_index=False)['Dollars'].sum().sort_values(by='Dollars',ascending=False)[:40])
fig_dist_sales = px.bar(top_custs,
       x = 'Customer',
       y = 'Dollars',
    title='<b>Top Individual Customers</b>',
    height=500,
    template = template,
    labels={'Customer':'',
            'Dollars':'<b>$USD</b>'},
    opacity=.6,        
    color = 'Market Segment').update_layout(showlegend=False,title_x=0.5)#,margin=dict(l=20, r=20, t=80, b=20),paper_bgcolor="LightGrey")
fig_dist_sales.update_yaxes(tick0=0,dtick=250000)

# parent distributor bar
top_parents = pd.DataFrame(df_selection[df_selection["Invoice Date"].dt.year == 2023].groupby(['Parent Customer','Market Segment'],as_index=False)['Dollars'].sum().sort_values(by='Dollars',ascending=False)[:20])
fig_parent_sales = px.bar(top_parents,
                          x = 'Parent Customer',
                          y = 'Dollars',
                          title='<b>Top Parent Customers</b>',
                          template = template,
                          labels={'Parent Customer':'',
                                'Dollars':'<b>$USD</b>'},
                          height=500,
                          opacity = .6,
                          color = 'Market Segment').update_layout(showlegend=False, title_x=0.5)#,margin=dict(l=20, r=20, t=80, b=20),paper_bgcolor="LightGrey")
fig_parent_sales.update_yaxes(tick0=0,dtick=500000)

# ---- CREATE TWO MORE COLUMNS AND PLACE GRAPHS ----
blank_left, left_column, right_column, blank_right = st.columns([.2,2.2,2.6,.2])
left_column.plotly_chart(fig_parent_sales, theme = 'streamlit', use_container_width=True)
right_column.plotly_chart(fig_dist_sales, theme = 'streamlit', use_container_width=True)

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)