import numpy as np
import streamlit as st
import pandas as pd
import datetime

###############
# COLOR DICTIONARIES
market_segment_dict = {
    'Vending': 'rgb(56,149,73)',
    'Grocery': 'rgb(248,184,230)',
    'Alternate Retail': 'rgb(46,70,166)',
    'Canada': 'rgb(204,208,221)',
    'Online': 'rgb(106,87,63)',
    'Other': 'rgb(200,237,233)',
    'Convenience': 'rgb(233,81,46)',
    'Broadline Distributor': 'rgb(233,152,19)',
    'Samples': 'rgb(141,62,92)'
    }

sale_origin_dict = {
    'Dot': 'rgb(81, 121, 198)',
    'Unleashed': 'rgb(239, 83, 80)'
}

market_legend_dict = {
    'Vending': 'Vending',
    'Grocery': 'Grocery',
    'Alternate Retail': 'Alt Retail',
    'Canada': 'Canada',
    'Online': 'Online',
    'Other': 'Other',
    'Convenience': 'Convenience',
    'Broadline Distributor': 'Broadline',
    'Samples': 'Samples'
    }