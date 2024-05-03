import streamlit as st
import json
import time
import streamlit.components.v1 as components
from sec_edgar_downloader import Downloader as SecEdgarDownloader
from sec_downloader.download_storage import DownloadStorage
from utility.functions import getSummary, getYear, genGemini2, genGeminiFigures, dictCombined

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


combined_section1A = ""
with st.spinner('Fetching Risk Factors related information from Item 1A of SEC 10-K filings'):
    block = st.empty()
    for path, content in storage.get_file_contents():
        year = getYear(path)
        combined_section1A += getSummary(content, 1)
        block.write(f"&nbsp; &nbsp; &nbsp; &nbsp; Compiling data for year {year}")
        time.sleep(5)   # cause time delay to avoid Rate Limit Error on API calls

block.write(" ")
summary = genGemini2(combined_section1A)
st.markdown(summary)
st.markdown('#')


combined_section7_metrics = {}
with st.spinner('Fetching financial data from Item 7 of SEC 10-K filings'):
    block = st.empty()
    for path, content in storage.get_file_contents():
        time.sleep(15)    # cause time delay to avoid Rate Limit Error on API calls
        year = getYear(path)
        combined_section7_metrics[year] = genGeminiFigures(content)
        block.write(f"&nbsp; &nbsp; &nbsp; &nbsp; Compiling data for year {year}")
block.write(" ")

mergeddata = dictCombined(combined_section7_metrics)


if "GAAP diluted earnings per share" in mergeddata and "Adjusted diluted earnings per share" in mergeddata:
    temp_dict = {
        "GAAP diluted earnings per share": mergeddata["GAAP diluted earnings per share"],
        "Adjusted diluted earnings per share": mergeddata["Adjusted diluted earnings per share"]
    }
    st.bar_chart(temp_dict, height=300)

if "Net sales" in mergeddata and "Net earnings" in mergeddata:
    temp_dict = {
        "Net sales": mergeddata["Net sales"],
        "Net earnings": mergeddata["Net earnings"]
    }
    st.markdown('<h5 style="text-align: center;">Trend of Net Sales and Net Earnings</h5>', unsafe_allow_html=True)
    st.line_chart(temp_dict, height=300)


if "Total revenue" in mergeddata:
    st.markdown('<h5 style="text-align: center;">Trend of Total Revenue of Company</h5>', unsafe_allow_html=True)
    st.line_chart(mergeddata["Total revenue"], height=300)

if "Operating income" in mergeddata:
    st.markdown('<h5 style="text-align: center;">Trend of Operating Income</h5>', unsafe_allow_html=True)
    st.line_chart(mergeddata["Operating income"], height=300)

if "Depreciation and amortization" in mergeddata:
    st.markdown('<h5 style="text-align: center;">Trend of Depreciation and amortization Rates</h5>', unsafe_allow_html=True)
    st.line_chart(mergeddata["Depreciation and amortization"], height=300)

if "Comparable sales" in mergeddata and "Comparable store originated sales" in mergeddata and "Comparable digital originated sales" in mergeddata:
    temp_dict = {
        "Comparable sales": mergeddata["Comparable sales"],
        "Comparable store originated sales": mergeddata["Comparable store originated sales"],
        "Comparable digital originated sales": mergeddata["Comparable digital originated sales"]
    }
    st.bar_chart(temp_dict, height=300)
