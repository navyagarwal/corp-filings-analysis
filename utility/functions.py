import json
import os


'''
The company_tickers.json is retrieved from https://www.sec.gov/files/ and a dictionary of company tickers and titles is created for easy lookup.
'''
def create_ticker_title_dict(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    ticker_title_dict = {company['ticker']: company['title'] for company in data.values()}
    output_file_path = os.path.join(os.path.dirname(json_file_path), 'ticker_title_dict.json')
    with open(output_file_path, 'w') as outfile:
        json.dump(ticker_title_dict, outfile, indent=4)
    print(f"Ticker:title dictionary created and saved as {output_file_path}")
