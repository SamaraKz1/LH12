"""
UI for running product search in database by user input. 

Run command from inside folder:
>> streamlit run ui.py
"""

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial.distance import pdist, cdist, squareform

from gsheetsdb import connect

# Connect to Google Sheets
def get_df(url):
    gsheet_url = st.secrets[url]
    conn = connect()
    print('yes')
    rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
    print('yes')
    df = pd.DataFrame(rows)
    return df


#data = get_df("gsheet_url_data")

gsheet_url = "https://docs.google.com/spreadsheets/d/1J85lbEUpc4GaERN4DQA-b6nfATQDjauJOH7IfnFmZ1M/edit?usp=sharing"
conn = connect()
rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')

data = = pd.DataFrame(rows)

descriptions = sorted(set(data['DESCRIPTION']))
vectorizer = CountVectorizer(input='content', max_features=2500)
wordcounts = vectorizer.fit_transform(descriptions).toarray()

#----------------------TITLES------------------
st.set_page_config(page_title="LH12 Price Recommendation", layout="wide", page_icon='📝') 
st.title("Recommendation for substitute product")

#--------------------- SIDEBAR ----------------

st.sidebar.title("Product Description")
category = st.sidebar.selectbox("Select category group area", ['Site Products & Logistics', 'IT (Server & Storage)'])

description = st.sidebar.selectbox("Select description", data['DESCRIPTION_TEXT'].unique())

list_specifications = data[data['DESCRIPTION_TEXT']==description]['DESCRIPTION'].unique()
product = st.sidebar.selectbox("Select specifications", list_specifications)

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

st.write(" The product info for the selected specification:")

#if category == 'Site Products & Logistics':

st.dataframe(data[(data['DESCRIPTION']==product)].reset_index(drop=True).style.format({"LOCAL_PRICE": "{:.2f}"}))

st.write(""" ## 📊 Substitude products: """)
#distances.index = distances.columns

n_neigh = st.selectbox("Number of substitude products to recommend", [i+1 for i in range(20)])

idx = descriptions.index(product)


distances = cdist(wordcounts[wordcounts].reshape(1,-1), wordcounts, metric='cosine')
distances = pd.DataFrame(distances, index=descriptions, columns = ['Distance']).reset_index().rename(columns = {'index':'PRODNO'})
neighbors = distances.nsmallest(n_neigh+1, 'Distance')


neigh_prod = pd.merge(neighbors, data, on=['DESCRIPTION'], how='in').sort_values('Distance').reset_index(drop=True)

st.write(neigh_prod)

#for i in range(len(neighbors)):
#    neigh_prod.loc[neigh_prod['DESCRIPTION'] == neighbors.index[i], 'Distance'] = neighbors.values[i]

#neigh_prod = neigh_prod.sort_values('Distance').reset_index(drop=True)

#st.dataframe(neigh_prod.style.format({"LOCAL_PRICE": "{:.2f}", "Distance": "{:.3f}"}))

#------------------ Find similarities -----------------


