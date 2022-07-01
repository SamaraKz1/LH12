import numpy as np
import pandas as pd
import streamlit as st

#from gsheetsdb import connect

st.title("My First Web App")

#st.title("Connect to Google Sheets")
gsheet_url_data = st.secrets["gsheet_url_data"]
#conn = connect()
#rows = conn.execute(f'SELECT * FROM "{gsheet_url_data}"')
#df_gsheet = pd.DataFrame(rows)
#st.write(df_gsheet)
st.write(gsheet_url_data)