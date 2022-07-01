import numpy as np
import pandas as pd
import streamlit as st

from gsheetsdb import connect

st.title("My First Streamlit Web App")

st.title("Connect to Google Sheets")
gsheet_url_data = "https://docs.google.com/spreadsheets/d/1Bk-eHoZtRuRH9bsgELzMxy-L22r6qNRbHzI4ztvkhrw/edit?usp=sharing"

conn = connect()
rows = conn.execute(f'SELECT * FROM "{gsheet_url_data}"')
df_gsheet = pd.DataFrame(rows)
st.write(df_gsheet)