import os
import streamlit as st
import json
import streamlit.components.v1 as components
from sec_api import QueryApi, ExtractorApi

queryApi = QueryApi(api_key='1a95cc8d9766f3a6968e5ec2b04bc08697b08a3199175cbefd4be5171e062072')

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
        query = {
            "query": f"ticker:{ticker[0]} AND formType:\"10-K\"",
            "from": "0",
            "size": "10",
            "sort": [{ "filedAt": { "order": "desc" }}]
        }

        response = queryApi.get_filings(query)
        url_list = {item["filedAt"]: item["linkToHtml"] for item in response["filings"]}
        print(url_list)

    else:
        st.write('No ticker found for the selected company')


for date, url in url_list.items():
    extractorApi = ExtractorApi("1a95cc8d9766f3a6968e5ec2b04bc08697b08a3199175cbefd4be5171e062072")
    section7_text = extractorApi.get_section(url, "7", "text")
    st.write(date)
    st.write(section7_text)