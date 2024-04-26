import os
import streamlit as st
import json

ticker_title_file_path = "utility/ticker_title_dict.json"
with open(ticker_title_file_path, 'r') as file:
    ticker_title_dict = json.load(file)

with st.sidebar:
    option = st.selectbox(
        'Company Name',
        list(ticker_title_dict.values())
    )
    ticker = [key for key, value in ticker_title_dict.items() if value == option]
    if ticker:
        st.write('Ticker:', ticker[0])
    else:
        st.write('No ticker found for the selected company')