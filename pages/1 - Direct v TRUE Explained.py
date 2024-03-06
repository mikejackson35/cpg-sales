import streamlit as st

st.set_page_config(page_title='Direct vs TRUE',
                   page_icon='assets/Nevil.png',
                   layout='wide')

st.sidebar.title('Direct Sales')
st.sidebar.markdown('Dot Sales Realized upon Purchase From AWAKE')
st.sidebar.title('TRUE Sales')
st.sidebar.markdown('Dot Sales Realized upon Purchase From Dot')

tab1, tab2 = st.tabs([':red[Direct]', ':orange[TRUE]'])
with tab1:
    st.image(r"assets\direct_sales.png", use_column_width=None)
with tab2:
    st.image(r"assets\TRUE_sales.png", use_column_width=None)

st.markdown("""
<style>
            
[data-baseweb="tab-list"] {
    gap: 4px;
}

[data-baseweb="tab"] {
    height: 40px;
    width: 625px;
    white-space: pre-wrap;
    background-color: #A29F99;
    border-radius: 4px 4px 0px 0px;
    gap: 3px;
    padding-top: 8px;
    padding-bottom: 8px;
}
            
[data-testid="stMarkdownContainer"] p {font-size:1.5rem;
    }
            
</style>
        """, unsafe_allow_html=True)