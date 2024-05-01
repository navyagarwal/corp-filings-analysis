import json
import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup


'''
The company_tickers.json is retrieved from https://www.sec.gov/files/ and a dictionary of company tickers and titles is created for easy lookup.
'''
def _create_ticker_title_dict(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    ticker_title_dict = {company['ticker']: company['title'] for company in data.values()}
    output_file_path = os.path.join(os.path.dirname(json_file_path), 'ticker_title_dict.json')
    with open(output_file_path, 'w') as outfile:
        json.dump(ticker_title_dict, outfile, indent=4)
    print(f"Ticker:title dictionary created and saved as {output_file_path}")

def getSummary(raw_10k):
    section7Text = _getSection7Text(raw_10k)
    return _summarize(section7Text)

def _getSection7Text(raw_10k):
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    type_pattern = re.compile(r'<TYPE>[^\n]+')
    doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]
    document = {}
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type == '10-K':
            document[doc_type] = raw_10k[doc_start:doc_end]
    regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(7|7A)\.{1})|(ITEM\s(7|7A)\.{1})')
    matches = regex.finditer(document['10-K'])
    test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])
    test_df.columns = ['item', 'start', 'end']
    test_df['item'] = test_df.item.str.lower()
    test_df.replace('&#160;',' ',regex=True,inplace=True)
    test_df.replace('&nbsp;',' ',regex=True,inplace=True)
    test_df.replace(' ','',regex=True,inplace=True)
    test_df.replace('\.','',regex=True,inplace=True)
    test_df.replace('>','',regex=True,inplace=True)
    pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
    pos_dat.set_index('item', inplace=True)
    item_7_raw = document['10-K'][pos_dat['start'].loc['item7']:pos_dat['start'].loc['item7a']]
    item_7_content = BeautifulSoup(item_7_raw, 'lxml')
    return item_7_content.get_text("\n\n")[0:]

def _summarize(section7Text):
    API_TOKEN = "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"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    data = query(
        {
            "inputs": section7Text,
            "parameters": {"do_sample": False},
        }
    )
    return data[0]['summary_text']