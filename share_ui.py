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

st.set_page_config(page_title="LH12 Price Recommendation", layout="wide", page_icon='📝') 


@st.cache(allow_output_mutation=True, hash_funcs={pd.DataFrame: lambda _: None})
def get_df(gsheet_url):
    conn = connect()
    rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
    df = pd.DataFrame(rows)
    return df



data = get_df(st.secrets["gsheet_url_swb"])
descriptions = sorted(set(data['DESCRIPTION']))
vectorizer = CountVectorizer(input='content', max_features=2500)
wordcounts = vectorizer.fit_transform(descriptions).toarray()

#----------------------TITLES------------------
st.title("Recommendation for substitute product")

#--------------------- SIDEBAR ----------------

st.sidebar.title("Product Description")
category = st.sidebar.selectbox("Select category group area", ['Site Products & Logistics', 'IT (Server & Storage)'])

prod_desc = st.sidebar.selectbox("Select one", ['Product Number', 'Description'])
description = st.sidebar.selectbox("Select description", data['DESCRIPTION_TEXT'].unique())
list_specifications = data[data['DESCRIPTION_TEXT']==description]['DESCRIPTION'].unique()
product = st.sidebar.selectbox("Select specifications", list_specifications)


#============================ Body ==============================

st.write(" The product info for the selected specification:")

#if category == 'Site Products & Logistics':

st.dataframe(data[(data['DESCRIPTION']==product)].reset_index(drop=True).style.format({"LOCAL_PRICE": "{:.2f}"}))

st.write(""" ## 📊 Substitude products: """)

n_neigh = st.selectbox("Number of substitude products to recommend", [i+1 for i in range(20)])
st.write(
    """
    ${Note}$: Distnace is a metric that represents how different the substitude products are to the one you selected. \\
    It varies from 0 (most similar) to 1 (least similar).
    """
    )

idx = descriptions.index(product)

distances = cdist(wordcounts, wordcounts[idx].reshape(1,-1), metric='cosine')
distances = pd.DataFrame(distances, index=descriptions, columns = ['Distance']).reset_index().rename(columns = {'index':'DESCRIPTION'})
neighbors = distances.nsmallest(n_neigh+1, 'Distance')

neigh_prod = pd.merge(neighbors, data, on='DESCRIPTION', how='inner').sort_values('Distance').drop('DESCRIPTION_TEXT', axis=1).reset_index(drop=True)
st.dataframe(neigh_prod.style.format({"LOCAL_PRICE": "{:.2f}", "Distance": "{:.3f}"}))

st.write(""" ## 📊 Compare given products: """)

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

options = st.multiselect("Select mutiple descriptions to compare", data['DESCRIPTION'].unique())

if options:
    vectorizer = CountVectorizer(input='content', max_features=200)
    wordcounts = vectorizer.fit_transform(options).toarray()
    cosine_dist = pd.DataFrame(squareform(pdist(wordcounts, metric='cosine')), index=options, columns=options)
    st.write(cosine_dist)

#------------------ Find similarities -----------------


