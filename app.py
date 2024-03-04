import streamlit as st
from biz import Screener

st.set_page_config(page_title='Multiple Farmer', page_icon='🌱')
st.title('Multiple Farmer')
cols = st.columns(4)
cols[0].link_button('📌 GitHub',
                    'https://github.com/qus0in/multiple_farmer',
                    use_container_width=True)
cols[1].link_button('📌 Finviz',
                    'https://finviz.com/',
                    use_container_width=True)
st.image('multiple_farmer.png', use_column_width=True)

with st.spinner('Loading data...'):
    screener = Screener()
    ty, t1, t2 = screener.get_table()

col1, col2 = st.columns(2)
col1.header('In')
col1.dataframe(t1, use_container_width=True)
col2.header('Out')
col2.dataframe(t2, use_container_width=True)

st.header('Target Yield')
t3 = ty.loc[:, ['target_yield']]\
    .sort_values(by='target_yield',
                 ascending=False).T
for i in range(0, len(t3.columns), 5):
    st.dataframe(t3.iloc[:, i:i+5],
                 use_container_width=True,
                 hide_index=True)