"""
UI for running product search in database by user input. 

Run command from inside folder:
>> streamlit run ui.py
"""

from itertools import product
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


def word2vec(list_desc):
    vectorizer = CountVectorizer(input='content', max_features=500)
    wordcounts = vectorizer.fit_transform(descriptions).toarray()

    return wordcounts


def show_sidebar(df, prod_col, desc_col):
    if prod_desc == 'Product Number':
        prodno = st.sidebar.selectbox("Select product number", sorted(df[prod_col].unique()))
        prod_list = list(data_swb[df[prod_col]==prodno][desc_col])
        product = max(prod_list, key=len)
        
    elif prod_desc == 'Description':
        #description = st.sidebar.selectbox("Select description", df['DESCRIPTION_TEXT'].unique())
        #list_specifications = data_swb[data_swb['DESCRIPTION_TEXT']==description][desc_col].unique()
        #product = st.sidebar.selectbox("Select specifications", list_specifications)
        product = st.sidebar.selectbox("Select description", df[desc_col].unique())

    return product

data_swb = get_df(st.secrets["gsheet_url_swb"])
data_po = get_df(st.secrets["gsheet_url_po"])
descriptions = sorted(set(data_swb['DESCRIPTION']))


#----------------------TITLES------------------
st.title("Recommendation for substitute product")

#--------------------- SIDEBAR ----------------

st.sidebar.title("Product Description")
category = st.sidebar.selectbox("Select category group area", ['Site Products & Logistics', 'IT (Server & Storage)'])

prod_desc = st.sidebar.selectbox("Select filter", ['Product Number', 'Description'])

if category == 'Site Products & Logistics':
    product  = show_sidebar(data_swb, 'PRODNO', 'DESCRIPTION')
    
elif category == 'IT (Server & Storage)':
    product  = show_sidebar(data_po, 'MaterialWithoutRState', 'MaterialDesc')


#============================ Body ==============================

st.write(" The product info for the selected specification:")

if category == 'Site Products & Logistics':
    st.dataframe(data_swb[(data_swb['DESCRIPTION']==product)].reset_index(drop=True).style.format({"LOCAL_PRICE": "{:.2f}"}))
elif category == 'IT (Server & Storage)':
    st.dataframe(data_po[(data_po['MaterialDesc']==product)].reset_index(drop=True))

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

neigh_prod = pd.merge(neighbors, data, on='DESCRIPTION', how='inner').sort_values('Distance').drop(['DESCRIPTION_TEXT','DESCRIPTION_stem'], axis=1).reset_index(drop=True)
st.dataframe(neigh_prod.style.format({"LOCAL_PRICE": "{:.2f}", "Distance": "{:.3f}"}))


#------------------ Find similarities -----------------
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

if prod_desc == 'Product Number':
    products = st.multiselect("Select mutiple products to compare", sorted(data['PRODNO'].unique()))
    options = list(set(data[data['PRODNO'].isin(products)]['DESCRIPTION']))
    #options = list(data.iloc[pd.Index(data['PRODNO']).get_indexer(products)]['DESCRIPTION'].unique())

elif prod_desc == 'Description':
    options = st.multiselect("Select mutiple descriptions to compare", data['DESCRIPTION'].unique())

if options:
    st.write(options)
    vectorizer = CountVectorizer(input='content', max_features=200)
    wordcounts = vectorizer.fit_transform(options).toarray()
    cosine_dist = pd.DataFrame(squareform(pdist(wordcounts, metric='cosine')), index=options, columns=options)
    st.write(cosine_dist)




