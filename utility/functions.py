import streamlit as st
import json
import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import google.ai.generativelanguage as glm


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


'''
Get cleaned data from the 10K filing by specific section number and generate its summary
'''
def getSummary(raw_10ktext, sectionNumber):
    sectionText = _getSectionText(raw_10ktext, sectionNumber)
    return generateSummary(sectionText)


'''
Get sectionwise data from raw 10K filing and clean it using Regex and BeautifulSoup
'''
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
    test_df.replace('&#160;',' ',regex=True,inplace=True)
    test_df.replace('&nbsp;',' ',regex=True,inplace=True)
    test_df.replace(' ','',regex=True,inplace=True)
    test_df.replace('\.','',regex=True,inplace=True)
    test_df.replace('>','',regex=True,inplace=True)
    test_df.replace('-','',regex=True,inplace=True)
    test_df.replace('—','',regex=True,inplace=True)
    pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
    pos_dat.set_index('item', inplace=True)
    
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


'''
Extract year from the storage path name of the filing
'''
def getYear(path):
    path = str(path)
    yearTerm = path.split('/')[3]
    year = yearTerm.split('-')[1]
    year = "20"+year
    return year

'''
Generate summary from input text using Google Gemini API
'''
def generateSummary(input):
    GOOGLE_API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        f'''
        Generate a summary of financial risks faced by the company given following information from its 10K annual SEC filing:
        {input}
        '''
    )
    return response.text



'''
Generate response about trend of financial risks faced by the company pre, during and post COVID pandemic
'''
def summarizeTrends(input):
    GOOGLE_API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        f'''
        Write one paragraph each about the trend of financial risks faced by the company pre, during and post COVID pandemic given following information:
        {input}
        '''
    )
    return response.text


'''
Define object schema for function calling in Gemini
'''
financial_data_properties = {
    str(2017): glm.Schema(type=glm.Type.NUMBER),
    str(2018): glm.Schema(type=glm.Type.NUMBER),
    str(2019): glm.Schema(type=glm.Type.NUMBER),
    str(2020): glm.Schema(type=glm.Type.NUMBER),
    str(2021): glm.Schema(type=glm.Type.NUMBER),
    str(2022): glm.Schema(type=glm.Type.NUMBER),
    str(2023): glm.Schema(type=glm.Type.NUMBER),
    str(2024): glm.Schema(type=glm.Type.NUMBER)
}

financial_data = glm.Schema(
    type = glm.Type.OBJECT,
    properties = {
    'GAAP diluted earnings per share': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Adjusted diluted earnings per share': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Total revenue': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Comparable sales': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Comparable store originated sales': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Comparable digital originated sales': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Operating income': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Depreciation and amortization': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Net sales': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties),
    'Net earnings': glm.Schema(type=glm.Type.OBJECT, properties=financial_data_properties)
    }
)

get_financial_data = glm.FunctionDeclaration(
    name="get_financial_data",
    description="Get financial data for multiple years.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties= {
                "data": financial_data
        },
    )
)


'''
Generate a summary of financial metrics using function calling in Gemini API
'''
def generateFigures(raw_10k):
    input = _getSectionText(raw_10k, 7)
    GOOGLE_API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name='models/gemini-1.5-pro-latest', tools = [get_financial_data])
    response = model.generate_content(f"""
                    Please add the yearwise financial metric values to the database:
                                       {input}
                    """,
                    tool_config={'function_calling_config':'ANY'}
                )
    result = response.candidates[0].content.parts[0].function_call
    result = type(result).to_dict(result)
    print(type(result))
    return result

'''
Parse the yearwise financial metric information for visualization purpose
'''
def parseMetricInformation(dict):
    result = {}
    for key, value in dict.items():
        if "data" in value.get("args", {}):
            curr = value["args"]["data"]
            for metric, values in curr.items():
                if metric not in result:
                    result[metric] = {}
                result[metric].update(values)
    return result