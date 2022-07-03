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

#from gsheetsdb import connect

st.write('Hi')


