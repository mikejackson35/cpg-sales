import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt


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

sales_23 = int(all_sales[all_sales["Invoice Date"].dt.year == 2023].Dollars.sum())
sales_22 = int(all_sales[all_sales['Invoice Date'].dt.year == 2022].Dollars.sum())

# --- FILTERS AND SIDEBAR ----

year = st.sidebar.multiselect(
    label = 'Year',
    options=all_sales['Invoice Date'].dt.year.unique(),
    default=all_sales['Invoice Date'].dt.year.unique()
)

segment = st.sidebar.multiselect(
    label='Market Segment',
    options=all_sales['Market Segment'].unique(),
    default=all_sales['Market Segment'].unique(),
)

# line divider
st.markdown(" ")

# QUERY THE DATEFRAME BASED ON FILTER SELECTIONS
df_selection = all_sales[
    (all_sales['Invoice Date'].dt.year.isin(year)) &
    (all_sales['Market Segment'].isin(segment))
    ]

# theme used for charts
template = 'presentation'

# ---- TOP KPI's Row ----
# sales_23 = int(df_selection[df_selection["Invoice Date"].dt.year == 2023].Dollars.sum())
# sales_22 = int(df_selection[df_selection['Invoice Date'].dt.year == 2022]['Dollars'].sum())

def plus_minus(delta):
    if delta > 0:
        symbol = "+"
    else:
        symbol = ""
    return symbol

delta = sales_23 - sales_22
# yoy_chg_perc = plus_minus(delta) + f"{int(sales_23/sales_22*100-100)}%"
customer_count = int(df_selection.Customer.nunique())
sales_per_customer = int(df_selection.Dollars.sum() / customer_count)

############
df_selection.index = pd.to_datetime(df_selection['Invoice Date'],format = '%m/%d/%y')
mth_sales = df_selection.groupby(pd.Grouper(freq='M'))[['Dollars','Dollars Formatted']].sum()
mth_sales['Dollars'] = mth_sales['Dollars'].astype('int')

config = {'displayModeBar': False}

fig_mth_bar = px.bar(mth_sales,
        template='plotly_white',
        x= mth_sales.index,
        y='Dollars',
        color='Dollars',
        color_continuous_scale=px.colors.sequential.Oranges,
        labels = {'Invoice Date':' ','Dollars':'<b>$USD</b>'},
        text="Dollars",
        opacity=.8,
        hover_data=['Dollars'],
        title=' ',
        height=400
        ).update_coloraxes(showscale=False)
fig_mth_bar.update_traces(texttemplate='<b>%{text:$,}</b>',hovertext=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
fig_mth_bar.update_layout(title_x=0.5,hovermode="x")
fig_mth_bar.update_xaxes(tickmode='array',tickvals = mth_sales.index, ticktext=mth_sales.index.month_name())
fig_mth_bar.update_yaxes(tick0=0,dtick=250000)#,showticklabels=False)

nevil, bar_chart, blank = st.columns([1,8,1])
with nevil:
    st.markdown("####")
    st.markdown("####")
    st.markdown("####")
    st.markdown("####")
    st.markdown("####")
    nevil.image("assets/Nevil.png",width=150)
bar_chart.plotly_chart(fig_mth_bar, config=config,  theme = 'streamlit',legend=None, use_container_width=True)
blank.markdown("##")



# SIDEBAR
blank, col1, col2, col3 = st.columns([.75,1.2,1.2,1.2])
with blank:
    st.markdown(" ")
with col1:
    st.markdown('<h4>Sales</h4>', unsafe_allow_html=True)
    st.title(f"${int(df_selection.Dollars.sum()):,}")
with col2:
    st.markdown('<h4>Num of Customers</h4>', unsafe_allow_html=True)
    st.title(F"{customer_count:,}")
with col3:
    st.markdown('<h4>$/Customer</h4>', unsafe_allow_html=True)
    st.title(f"${sales_per_customer:,}")

# line divider
st.markdown("   ")
st.markdown("---")
st.markdown("   ")

# distributor bar
top_custs = pd.DataFrame(df_selection.groupby(['Customer','Market Segment'],as_index=False)['Dollars'].sum().sort_values(by='Dollars',ascending=False)[:40])
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
top_parents = pd.DataFrame(df_selection.groupby(['Parent Customer','Market Segment'],as_index=False)['Dollars'].sum().sort_values(by='Dollars',ascending=False)[:20])
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

# segment pie chart
seg_sales = df_selection.groupby('Market Segment',as_index=False)['Dollars'].sum().sort_values(by='Market Segment',ascending=False)
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
parent_bar, seg_pie,child_bar = st.columns(3)
with parent_bar:
    st.plotly_chart(fig_parent_sales, theme = 'streamlit', use_container_width=True)
with seg_pie:
    st.plotly_chart(fig_seg_sales, theme = 'streamlit', use_container_width=True)
with child_bar:
    st.plotly_chart(fig_dist_sales, theme = 'streamlit', use_container_width=True)


# line divider
st.markdown("---")

# WEEKLY SCATTER CHARTS
sales_per_week = df_selection.groupby(pd.Grouper(freq='W', key='Invoice Date'))['Dollars'].sum()
# sales_per_day_2023 = sales_per_day[sales_per_day.index.year==2023]

#all sales weekly scatter
fig_scatter_all = px.scatter(
    sales_per_week,
    x=sales_per_week.index,
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

st.markdown("##")
blank_left, chart, blank_right,  = st.columns([.5,2.8,.5])

blank_left.markdown("")
chart.plotly_chart(fig_scatter_all, theme = 'streamlit', use_container_width=True)
blank_right.markdown("")

# ---- REMOVE UNWANTED STREAMLIT STYLING ----
hide_st_style = """
            <style>
            Main Menu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
            
st.markdown(hide_st_style, unsafe_allow_html=True)