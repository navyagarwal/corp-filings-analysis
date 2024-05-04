# Financial Analysis in Retail: A Dive into Pandemic Impact

### Introduction
For this project, I focussed on the four major retail corporations of the US: Target, Home Depot, Costco, and Lowe&#39;s.

The initial motivation was to extract and analyze financial trends pre, during, and post-pandemic. However, the current progress of the project might not reflect much coherence to that due to difficulties faced with the extraction of financial metric values from filings, computational resource limitations, and time constraints. 

Nevertheless, the project lays a solid groundwork for further work in this direction.

by retrieving SEC 10-K filings, extracting and cleaning sectionwise text, and passing the text to LLM inference API for .

## Methodology

### Tools and Technologies Used:
- <b>Programming Language</b>: Python is my preferred development language. It is also very suitable for this project because of rich ecosystem of libraries suitable for data analysis, visualization and interface with various LLM APIs.
- <b>Deployment Platform</b>: Streamlit was chosen primarily because it allows very quick and easy deployment. I considered using Plotly Dash too, and hosting the project on Heroku but that did not fit the tight time constraints.
- <b>API for 10K Filing Retrieval</b>: [sec-edgar-downloader](https://sec-edgar-downloader.readthedocs.io/en/latest/), as recommended, was initially my choice, but it proved computationally expensive as it downloaded all documents, some of which were hundreds of MBs. Handling storage and deleting temporary files became complicated. Then I tried [SEC API](https://sec-api.io/), it seemed very promising initially, but I realized the next day that only the first 100 calls were free. Finally, I found [sec-edgar-api](https://sec-edgar-api.readthedocs.io/en/latest/) (a wrapper on sec-edgar-downloader) that allowed storing files in memory instead of downloading to disk, which proved very helpful. Ultimately, this was the one I used.
- <b>LLM Inference API</b>: While I had some experience with basic NLP tasks from my academic curriculum, this project marked my first encounter with an LLM. Initially, I struggled with numerous Hugging Face models like [Facebook BART CNN](https://huggingface.co/facebook/bart-large-cnn), [Roberta Base Squad 2](https://huggingface.co/deepset/roberta-base-squad2), [Distilbart CNN](https://huggingface.co/sshleifer/distilbart-cnn-12-6) among many others, for summarization and question-answering tasks. However, the results were suboptimal, largely because the models weren't trained on finance-specific data. I attempted to use the OpenAI API, but encountered issues with my API key, likely requiring purchasing credits. Eventually, I turned to the Google Gemini API, which yielded good results, and I didn't look back.
- <b>Tools for Text Preprocessing</b>: Text preprocessing was labor-intensive, involving extensive regex, BeautifulSoup, and parsing to extract required section items from filings and convert them from HTML to text format.

### Screen recording of the project
(The page takes around 3 to 4 minutes to load completely, this video has been sped up in certain places)

https://github.com/navyagarwal/corp-filings-analysis/assets/82928853/96230ea0-2674-42c1-8bad-bef63210990f



### Challenges Encountered:
- <b>Insight Extraction</b>: Extraction of useful information, especially financial metric figures and pandemic-related trends proved to be a challenge. LLMs pretrained on relevant data combined with better text pre-processing (like extracting tabular data) should give better results. 
- <b>Computational Resource Limitations</b>: Since I was relying on free credits and compute power, processing large datasets and complex analysis was challenging due to resource constraints. The page loading time could be reduced by introducing parallel programming to make several API calls at once.
- <b>Time Constraints</b>: The time that I could dedicate to the project was constrained which impacted the quality of analysis achieved.

### Future Work
Although the current state of the project does not fully reflect the initial objectives, there is significant potential for future work in this direction. With additional resources and time, further analysis could provide valuable insights into the financial performance of these retail giants across different periods, especially in response to significant events like the COVID-19 pandemic.
