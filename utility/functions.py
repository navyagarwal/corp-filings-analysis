import json
import os
import re
import pandas as pd
import requests
import string
import numpy as np
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

def getSummary(raw_10k, item):
    sectionText = _getSectionText(raw_10k, item)
    return _summarize(sectionText)

def _getSectionText(raw_10k, item):
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
    regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7|7A)\.{1})|(ITEM\s(1A|1B|7|7A)\.{0, 1})|(Item(\s|&#160;|&nbsp;)(1A|1B|7|7A)\s(-|—))|(Item(\s|&#160;|&nbsp;)(1A|1B|7|7A)(-|—))')
    matches = regex.finditer(document['10-K'])
    test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])
    test_df.columns = ['item', 'start', 'end']
    test_df['item'] = test_df.item.str.lower()
    # print(test_df)
    test_df.replace('&#160;',' ',regex=True,inplace=True)
    test_df.replace('&nbsp;',' ',regex=True,inplace=True)
    test_df.replace(' ','',regex=True,inplace=True)
    test_df.replace('\.','',regex=True,inplace=True)
    test_df.replace('>','',regex=True,inplace=True)
    test_df.replace('-','',regex=True,inplace=True)
    test_df.replace('—','',regex=True,inplace=True)
    pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
    pos_dat.set_index('item', inplace=True)
    # print(pos_dat)
    
    if(item == 1):
        if(pos_dat['start'].loc['item1a'] < pos_dat['start'].loc['item1b']):
            item_1_raw = document['10-K'][pos_dat['start'].loc['item1a']:pos_dat['start'].loc['item1b']]
        else:
            item_1_raw = document['10-K'][pos_dat['start'].loc['item1b']:pos_dat['start'].loc['item1a']]    
        item_content = item_1_raw     
        item_content = BeautifulSoup(item_content, 'lxml').get_text("\n\n")[0:]
        item_content = re.sub(r'\d+', '', item_content)
        item_content = "".join([char for char in item_content if char not in "#$%&()*+,/:;<=>?@[\]^_`{|}~"]) 
        item_content = re.sub('\s+', ' ', item_content).strip()
    
    elif(item == 7):
        if(pos_dat['start'].loc['item7'] < pos_dat['start'].loc['item7a']):
            item_7_raw = document['10-K'][pos_dat['start'].loc['item7']:pos_dat['start'].loc['item7a']]
        else:
            item_7_raw = document['10-K'][pos_dat['start'].loc['item7a']:pos_dat['start'].loc['item7']]   
        item_content = item_7_raw
        item_content = BeautifulSoup(item_content, 'lxml').get_text("\n\n")[0:]
        item_content = "".join([char for char in item_content if char not in "#&()*+,/:;<=>?@[\]^_`{|}~"]) 
        item_content = re.sub('\s+', ' ', item_content).strip()
        
    return item_content

def _summarize(sectionText):
    API_TOKEN = "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"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    data = query(
        {
            "inputs": sectionText,
            "parameters": {"do_sample": False},
            "options": {"wait_for_model": True}
        }
    )
    return data[0]['summary_text']

def getYear(path):
    path = str(path)
    yearTerm = path.split('/')[3]
    year = yearTerm.split('-')[1]
    year = "20"+year
    return year

def getFigure(raw_10k, year):
    section7Text = _getSectionText(raw_10k, 7)
    API_TOKEN = "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"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    data = query(
        {
            "inputs": {
                "question": f"How much is the earnings per share in {year}?",
                "context": section7Text,
            },
            "options": {"wait_for_model": True}
        }
    )
    print(data)
    return data["answer"]


def cleanFigures(dict):
    for key, value in dict.items():
        value = value.replace('-', ' ')
        list = value.split(' ')
        list = [x for x in list if not x.isalpha()]
        try:
            value = list[-1]
            value = value.replace('$', '')
        except:
            value = np.nan
        if(float(value) > 40):
            value = np.nan
        dict[key] = value
    
    return dict