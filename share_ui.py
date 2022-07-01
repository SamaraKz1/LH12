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
gsheet_url = st.secrets["gsheet_url_data"]
conn = connect()
rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
data = pd.DataFrame(rows)


