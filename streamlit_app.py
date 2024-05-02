import streamlit as st
import json
import streamlit.components.v1 as components
from sec_edgar_downloader import Downloader as SecEdgarDownloader
from sec_downloader.download_storage import DownloadStorage
from utility.functions import getSummary, getFigure, getYear, cleanFigures

retail_company_tickers_file_path = "utility/retail_company_tickers.json"
with open(retail_company_tickers_file_path, 'r') as file:
    retail_company_tickers_dict = json.load(file)

with st.sidebar:
    option = st.selectbox(
        '&nbsp; Select Company Name',
        list(retail_company_tickers_dict.values())
    )
    ticker = [key for key, value in retail_company_tickers_dict.items() if value == option]
    if ticker:
        st.write('&nbsp; Ticker:', ticker[0])
        storage = DownloadStorage()
        with storage as path:
            dl = SecEdgarDownloader("MyCompanyName", "email@example.com", path)
            dl.get("10-K", ticker[0], limit=5)

    else:
        st.write('No ticker found for the selected company')


st.title(retail_company_tickers_dict[ticker[0]])
st.divider()
st.subheader("Summary of Risk Factors associated with the Company")
raw_10k = storage.get_file_contents()[0].content
summary = getSummary(raw_10k, 1)
st.write(summary)

dict = {}
for path, content in storage.get_file_contents():
    year = getYear(path)
    figure = getFigure(content, year)
    dict[year] = figure

st.markdown('#')
st.markdown('<h5 style="text-align: center;">Trend of Earnings Per Share over the last 5 Years</h5>', unsafe_allow_html=True)
# st.caption('Trend of Earnings Per Share over the last 5 Years')
dict = cleanFigures(dict)
st.bar_chart(dict, height=300)