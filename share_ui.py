"""
UI for product search engine and recommendation for substitude products. 

'https://samarakz1-lh12-share-ui-k4jh8v.streamlitapp.com/'
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

@st.cache(allow_output_mutation=True)
def word2vec(descs):
    list_desc = sorted(set(descs))
    vectorizer = CountVectorizer(input='content', max_features=2000)
    wordcounts = vectorizer.fit_transform(list_desc).toarray()

    return wordcounts


def show_sidebar(df, prod_col, desc_col):
    if prod_desc == 'Product Number':
        prodno = st.sidebar.selectbox("Select product number", sorted(df[prod_col].unique()))
        prod_list = list(df[df[prod_col]==prodno][desc_col])
        product = max(prod_list, key=len)
        
    elif prod_desc == 'Description':
        product = st.sidebar.selectbox("Select description", sorted(df[desc_col].unique()))

    return product

data_swb = get_df(st.secrets["gsheet_url_swb"])
data_po = get_df(st.secrets["gsheet_url_po"])
swb_words = word2vec(data_swb['DESCRIPTION'])
po_words = word2vec(data_po['MaterialDesc'])


#==========================TITLES=======================
st.title("Recommendation for substitute product")
st.write(" The product info for the selected specification:")
#==========================SIDEBAR & Body===============

st.sidebar.title("Product Description")
category = st.sidebar.selectbox("Select category group area", ['Site Products & Logistics', 'IT (Server & Storage)'])

prod_desc = st.sidebar.selectbox("Select filter", ['Product Number', 'Description'])

if category == 'Site Products & Logistics':
    swb_product = show_sidebar(data_swb, 'PRODNO', 'DESCRIPTION')
    st.dataframe(
        data_swb[(data_swb['DESCRIPTION']==swb_product)].drop(['DESCRIPTION_stem','DESCRIPTION_TEXT'], axis=1).reset_index(drop=True).style.format({"LOCAL_PRICE": "{:.2f}"})
        )
    
elif category == 'IT (Server & Storage)':
    po_product = show_sidebar(data_po, 'MaterialWithoutRState', 'MaterialDesc')
    st.dataframe(data_po[(data_po['MaterialDesc']==po_product)].reset_index(drop=True))


#============================Find Substitude Products==============================


st.write(""" ## 📊 Substitude products: """)

n_neigh = st.selectbox("Number of substitude products to recommend", [i+1 for i in range(20)])
st.write(
    """
    Note: Distnace is a metric that represents how different the substitude products are to the one you selected. \\
    It varies from 0 (most similar) to 1 (least similar).
    """
    )

def find_neighbors(df, product, wordcounts):
    descriptions = sorted(set(df))
    idx = descriptions.index(product)

    distances = cdist(wordcounts, wordcounts[idx].reshape(1,-1), metric='cosine')
    distances = pd.DataFrame(
        distances, index=descriptions, columns = ['Distance']
        ).reset_index().rename(columns = {'index':df.name})
    neighbors = distances.nsmallest(n_neigh+1, 'Distance')

    return neighbors


def merge_dfs(df1, df2, key):
    neigh_prod = pd.merge(df1, df2, on=key, how='inner').sort_values('Distance').reset_index(drop=True)
    return neigh_prod

if category == 'Site Products & Logistics':
    df_neighbors = find_neighbors(data_swb['DESCRIPTION'], swb_product, swb_words)
    neigh_prod = merge_dfs(df_neighbors, data_swb.drop(['DESCRIPTION_stem','DESCRIPTION_TEXT'], axis=1), 'DESCRIPTION')

    st.dataframe(neigh_prod.style.format({"LOCAL_PRICE": "{:.2f}", "Distance": "{:.3f}"}))

elif category == 'IT (Server & Storage)':
    df_neighbors = find_neighbors(data_po['MaterialDesc'], po_product, po_words)
    neigh_prod = merge_dfs(df_neighbors, data_po, 'MaterialDesc')

    st.dataframe(neigh_prod.style.format({"Distance": "{:.3f}"}))

#=========================Find similarities===========================
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


def get_comparison(df, prod_desc, prod_col, desc_col):
    if prod_desc == 'Product Number':
        products = st.multiselect("Select mutiple products to compare", sorted(df[prod_col].unique()))
        options = list(set(df[df[prod_col].isin(products)][desc_col]))

    elif prod_desc == 'Description':
        options = st.multiselect("Select mutiple descriptions to compare", df[desc_col].unique())
    
    if options:
        st.write(df[df[desc_col].isin(options)].drop(
            ['DESCRIPTION_stem','DESCRIPTION_TEXT'], axis=1)
            ).reset_index(drop=True)

    return options


def calculate_distance(options): 
    vectorizer = CountVectorizer(input='content', max_features=1000)
    wordcounts = vectorizer.fit_transform(options).toarray()
    cosine_dist = pd.DataFrame(squareform(pdist(wordcounts, metric='cosine')), index=options, columns=options)
    st.write(cosine_dist)


if category == 'Site Products & Logistics':
    options = get_comparison(data_swb, prod_desc, 'PRODNO', 'DESCRIPTION_stem')

elif category == 'IT (Server & Storage)':
    options = get_comparison(data_po, prod_desc, 'MaterialWithoutRState', 'MaterialDesc')    

if options:
        calculate_distance(options)






