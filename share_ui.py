"""
UI for running product search in database by user input. 

Run command from inside folder:
>> streamlit run ui.py
"""

import numpy as np
import pandas as pd
import streamlit as st

from gsheetsdb import connect

st.set_page_config(page_title="LH12 Price Recommendation", layout="wide", page_icon='📝') 
st.title("Recommendation for substitute product")

# Connect to Google Sheets
def get_df(url):
    gsheet_url = st.secrets[url]
    conn = connect()
    rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
    df = pd.DataFrame(rows)
    return df


data = get_df("gsheet_url_data")
distances = get_df("gsheet_url_cos1")

#--------------------- SIDEBAR ----------------

st.sidebar.title("Product Description")
description_txt = st.sidebar.selectbox("Select category group area", ['Site Products & Logistics', 'IT (Server & Storage)'])

description_txt = st.sidebar.selectbox("Select description", data['DESCRIPTION_TEXT'].unique())

list_specifications = data[data['DESCRIPTION_TEXT']==description_txt]['DESCRIPTION'].unique()
prod_data = st.sidebar.selectbox("Select specifications", list_specifications)

st.sidebar.title("Product Comparison")
st.markdown(
    """
<style>
span[data-baseweb="tag"] {
  background-color: grey !important;
}
</style>
""",
    unsafe_allow_html=True,
)
options = st.sidebar.multiselect("Select mutiple descriptions to compare", data['DESCRIPTION'].unique())

#---------------------- Body ------------------

#st.write(" The product info for the selected description:")
#st.dataframe(data[(data['DESCRIPTION_TEXT']==description_txt)].reset_index(drop=True).style.format({"LOCAL_PRICE": "{:.2f}"}))

st.write(" The product info for the selected specification:")
st.dataframe(data[(data['DESCRIPTION']==prod_data)].reset_index(drop=True).style.format({"LOCAL_PRICE": "{:.2f}"}))

st.write(""" ## 📊 Substitude products: """)

#distances.index = distances.columns

#n_neigh = st.selectbox("Number of substitude products to recommend", [i+1 for i in range(20)])

#neighbors = distances.nsmallest(n_neigh+1, prod_data)[prod_data]
#neigh_prod = data[data['DESCRIPTION'].isin(list(neighbors.index))].reset_index(drop=True)

#for i in range(len(neighbors)):
#    neigh_prod.loc[neigh_prod['DESCRIPTION'] == neighbors.index[i], 'Distance'] = neighbors.values[i]

#neigh_prod = neigh_prod.sort_values('Distance').reset_index(drop=True)

#st.dataframe(neigh_prod.style.format({"LOCAL_PRICE": "{:.2f}", "Distance": "{:.3f}"}))

#------------------ Find similarities -----------------


