import numpy as np
import streamlit as st
import pandas as pd
import datetime

###############
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

sale_origin_dict = {
    'dot': 'rgb(81, 121, 198)',
    'direct': 'rgb(239, 83, 80)'
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
    'Samples': 'Samples',
    'Spec Retail': 'Spec Retail'
    }