import numpy as np
import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import create_engine

# database connection

# db_password = "UnitCircle42!"
# db_user = "postgres"
# db_name = "dot"
# endpoint = "awakedb.cre3f7yk1unp.us-west-1.rds.amazonaws.com"

# connection_string = f"postgresql://{db_user}:{db_password}@{endpoint}:5432/{db_name}"
# engine = create_engine(connection_string)

conn = st.connection('dot', type ="sql")
engine = create_engine(conn)

# FUNCTION TO READ NEW UNL DATA, FIX COLUMN NAMES, APPEND POSTGRES DB
def add_new_unl(unl_download):
    new_unl_raw = pd.read_excel(unl_download,header=2)
    new_unl_raw = new_unl_raw.loc[:, ~new_unl_raw.columns.str.match('Unnamed')]     #remove 'Unnamed' column
    new_unl_raw.drop(new_unl_raw.tail(1).index,inplace=True)                        #remove unwanted headers and footers
    new_unl_raw.columns = ['order_num','order_date','req_date','completed_date',    #rename columns
                           'warehouse','customer_name','customer_type','product',
                           'product_group','status','quantity','sub_total']
    new_unl_raw.to_sql('unleashed_raw', engine, if_exists='append', index=False)    #send to database

# FUNCTION TO READ NEW DOT DATA, FIX COLUMN NAMES, APPEND POSTGRES DB
def add_new_dot(dot_download):
    new_dot_raw = pd.read_excel(dot_download, header=2)
    new_dot_raw.columns = ['supplier_name', 'product_line_number', 'product_line_desc',   #rename columns
           'buying_group_number', 'buying_group_name', 'customer_num',
           'customer_name', 'customer_shipping_city', 'customer_shipping_state',
           'customer_shipping_zip', 'customer_invoice_number', 'invoice_date',
           'customer_po_number', 'customer_order_number', 'prod_dot_number',
           'prod_mfg_number', 'item_upc', 'item_full_desc', 'qty_ordered',
           'qty_received', 'dollars', 'cust_ext_gross_weight',
           'cust_ext_net_weight', 'channel_num', 'channel_desc', 'segment_code',
           'segment_desc', 'tier_num', 'tier_desc', 'prod_line_sub_cat', 'dot_dc']
    new_dot_raw.to_sql('invoice_detail', engine, if_exists='append', index=False)         #send to database

### FUNCTION TAKING UNLEASHED_RAW TO UNLEASHED_CLEAN
def clean_unleashed():
    unleashed_raw = pd.read_sql("""
                                SELECT completed_date, customer_name, product, quantity, sub_total 
                                FROM unleashed_raw
                                ;""", 
                                con = engine)

    # add $ USD columns converted from CAD
    unleashed_raw['usd'] = unleashed_raw['sub_total']*.75
    # add origin of sale (dot or unleashed)
    unleashed_raw['sale_origin'] = 'unl'

    # assign market segments to each customer
    segment_table = pd.read_csv(r"C:\Users\mikej\Desktop\cpg-sales\data\customer_table.csv",usecols=('customer','market_segment')).set_index('customer')
    unleashed_raw.set_index('customer_name',inplace=True)
    unleashed_raw = unleashed_raw.merge(segment_table, how='left',left_index=True,right_index=True)

    # assign parent customers to customers
    cus_table = pd.read_csv(r"C:\Users\mikej\Desktop\cpg-sales\data\customer_table.csv",usecols=('customer','parent_customer')).set_index('customer')
    unleashed_raw = unleashed_raw.merge(cus_table, how='left',left_index=True,right_index=True).reset_index()

    # add year/month columns
    unleashed_raw['completed_date'] = pd.to_datetime(unleashed_raw['completed_date'])
    year_col = unleashed_raw.set_index(['completed_date']).index.year
    month_col = unleashed_raw.set_index(['completed_date']).index.month_name()
    unleashed_raw.insert(0,"month", month_col)
    unleashed_raw.insert(1,"year", year_col)
    
    unleashed_raw['completed_date'] = unleashed_raw['completed_date'].dt.date
    
    unleashed_raw.to_sql('unleashed_clean', engine, if_exists='replace', index=False)

### FUNCTION TAKING INVOICE DETAIL TO INVOICE CLEAN
def clean_dot():
    dot_raw = pd.read_sql("""
                            SELECT customer_name, invoice_date, item_full_desc, qty_received, dollars, segment_desc
                            FROM invoice_detail
                            ;""", 
                            con = engine)

    ## add canadian dollars column
    dot_raw['cad'] = round(dot_raw.dollars*1.33,2)

    ## add column to denote the dot table
    dot_raw['sale_origin'] = 'dot'

    # assign parent customers to customers
    cus_table = pd.read_csv(r"C:\Users\mikej\Desktop\cpg-sales\data\customer_table.csv",usecols=('customer','parent_customer')).set_index('customer')
    dot_raw.set_index('customer_name',inplace=True)
    dot_raw = dot_raw.merge(cus_table, how='left',left_index=True,right_index=True)

    # assign market segments to each parent customer
    segment_table = pd.read_csv(r"C:\Users\mikej\Desktop\cpg-sales\data\customer_table.csv",usecols=('customer','market_segment')).set_index('customer')
    dot_raw = dot_raw.merge(segment_table, how='left',left_index=True,right_index=True).reset_index()

    # add year/month columns
    dot_raw['invoice_date'] = pd.to_datetime(dot_raw['invoice_date'])
    year_col = dot_raw.set_index(['invoice_date']).index.year
    month_col = dot_raw.set_index(['invoice_date']).index.month_name()

    # # month & year columns
    dot_raw.insert(0,"month", month_col)
    dot_raw.insert(1,"year", year_col)

    # # final fix dtypes
    dot_raw = dot_raw.convert_dtypes()
    dot_raw['qty_received'] = dot_raw['qty_received'].astype('float')
    dot_raw['invoice_date'] = dot_raw['invoice_date'].dt.date

    dot_raw.drop(columns='segment_desc',inplace=True)
    dot_raw.to_sql('invoice_clean', engine, if_exists='replace', index=False)

### FUNCTION TO COMBINE UNLEASHED AND DOT OUTBOUNDS - CREATING LEVEL 2 SALES IN POSTGRES DATABASE
def get_level_2():
    dot = pd.read_sql('SELECT * FROM invoice_clean;', con = engine)
    unl = pd.read_sql('SELECT * FROM unleashed_clean;', con = engine)

    unl.columns = ['month','year','customer','date','item','qty','cad','usd','sale_origin','market_segment','parent_customer']
    dot.columns = ['month','year','customer','date','item','qty','usd','cad','sale_origin','parent_customer','market_segment']

    lvl2 = pd.concat([dot,unl]).sort_values(by='date',ascending=False).reset_index(drop=True)
    lvl2 = lvl2[lvl2.customer != 'DOT Foods, Inc.'].convert_dtypes()

    new_order = ['date', 'sale_origin', 'market_segment', 'parent_customer', 'customer', 'item', 'qty', 'usd', 'cad','month','year']

    for i,col in enumerate(new_order):
        tmp = lvl2[col]
        lvl2.drop(labels=[col],axis=1,inplace=True)
        lvl2.insert(i,col,tmp) 
        
    lvl2.to_sql('level_2', engine, if_exists='replace', index=False)