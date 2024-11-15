import streamlit as st

st.set_page_config(page_title='Direct vs TRUE',
                   page_icon='assets/Nevil.png',
                   layout='wide')

# CSS and PLOTLY CONFIGS
with open(r"styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.markdown("""
<style>

[data-baseweb="tab-list"] {
    gap: 4px;
}

[data-baseweb="tab"] {
    height: 50px;
    width: 655px;
    white-space: pre-wrap;
    background-color: #A29F99;
    # border-radius: 4px 4px 0px 0px;
    gap: 3px;
    padding-top: 8px;
    padding-bottom: 8px;
    font-weight:  1000;
}

.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
font-size:2rem;
}
            
</style>
        """, unsafe_allow_html=True)

st.sidebar.title('Direct Sales')
st.sidebar.markdown('Dot Sales Realized upon Purchase From AWAKE')
st.sidebar.title('TRUE Sales')
st.sidebar.markdown('Dot Sales Realized upon Purchase From Dot')

st.write('#')
tab1, tab2 = st.tabs(['Direct', ':black[True]'])
with tab1:
    st.image(r"./assets/direct.png", use_column_width='auto')
with tab2:
    st.image(r"./assets/true.png", use_column_width='auto')