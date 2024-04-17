import streamlit as st
import pandas as pd
import numpy as np

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title='Model Input',
                   page_icon='assets/Nevil.png',
                   layout='wide'
)

df = pd.DataFrame(
    "",
    index=range(1),
    columns=['out_1ago','out_2ago','in_1ago','in_2ago','fc_1ago','fc_2ago','inv_chg_1ago','inv_chg_2ago','dot_purchases'],
)

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True)

gb.configure_column('out_1ago',
    cellEditor='agRichSelectCellEditor',
    cellEditorParams={'values':["1","2","3"]},
    cellEditorPopup=True
)

gb.configure_grid_options(enableRangeSelection=True)


response = AgGrid(
    df,
    gridOptions=gb.build(),
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=True,
    theme='material'
)