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

st.write('yes')
#data = get_df("gsheet_url_data")

#gsheet_url = "https://docs.google.com/spreadsheets/d/1J85lbEUpc4GaERN4DQA-b6nfATQDjauJOH7IfnFmZ1M/edit?usp=sharing"
#conn = connect()
#rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')

#data = = pd.DataFrame(rows)



#for i in range(len(neighbors)):
#    neigh_prod.loc[neigh_prod['DESCRIPTION'] == neighbors.index[i], 'Distance'] = neighbors.values[i]

#neigh_prod = neigh_prod.sort_values('Distance').reset_index(drop=True)

#st.dataframe(neigh_prod.style.format({"LOCAL_PRICE": "{:.2f}", "Distance": "{:.3f}"}))

#------------------ Find similarities -----------------


