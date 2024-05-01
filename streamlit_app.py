import streamlit as st
import json
import streamlit.components.v1 as components
from sec_edgar_downloader import Downloader as SecEdgarDownloader
from sec_downloader.download_storage import DownloadStorage
from utility.functions import getSummary

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
        storage = DownloadStorage()
        with storage as path:
            dl = SecEdgarDownloader("MyCompanyName", "email@example.com", path)
            dl.get("10-K", ticker[0], limit=5)

    else:
        st.write('No ticker found for the selected company')

raw_10k = storage.get_file_contents()[0].content
summary = getSummary(raw_10k)
st.write(summary)