# Financial Analysis in Retail: A Dive into Pandemic Impact

### Introduction
For this project, I focussed on the four major retail corporations of the US: Target, Home Depot, Costco, and Lowe&#39;s.

The initial motivation was to extract information from the SEC 10-K filings and analyze financial trends pre, during, and post-pandemic.

However, the current progress of the project may not fully reflect the initial intentions. I faced challenges during extraction of financial metric values from filings due to computational power and time constraints. 

Nevertheless, the project lays a solid groundwork for further work in this direction.

### Why these insights?

Entire economies were caught off guard by the COVID-19 pandemic and faced serious financial consequences, it is reasonable to assume that pandemics are likely to persist.

Thus, studying financial trends in retail companies is particularly significant due to their direct connection to consumer behavior, economic trends, and market dynamics.

The performance of retail companies provide insights into both microeconomic factors affecting individual businesses and macroeconomic trends shaping the overall economy, making them crucial indicators for investors, policymakers, and analysts.

### Tools and Technologies Used:
- <b>Programming Language</b>: Python is my preferred development language. It is also suitable for this project because of its rich ecosystem of libraries available for data analysis, visualization and easy interface with various LLM APIs.
- <b>Deployment Platform</b>: The primary reason I used Streamlit is because it allows very quick and easy deployment. I considered building a dashboard using Plotly Dash initially, and hosting the project on a free cloud hosting service, but that would have required more time than was available.
- <b>API for 10K Filing Retrieval</b>: [sec-edgar-downloader](https://sec-edgar-downloader.readthedocs.io/en/latest/), as recommended, was initially my choice, but it proved computationally expensive as it downloaded all documents, some of which were hundreds of MBs. Handling storage and deleting temporary files became complicated. Then I tried [SEC API](https://sec-api.io/), it seemed very promising initially, but I realized the next day that only the first 100 calls were free. Finally, I found [sec-edgar-api](https://sec-edgar-api.readthedocs.io/en/latest/) (a wrapper on sec-edgar-downloader) that allowed storing files in memory instead of downloading to disk, which proved very helpful. Ultimately, this was the one I used.
- <b>LLM Inference API</b>: Initially, I experimented with numerous Hugging Face models like [Facebook BART CNN](https://huggingface.co/facebook/bart-large-cnn), [Roberta Base Squad 2](https://huggingface.co/deepset/roberta-base-squad2), [Distilbart CNN](https://huggingface.co/sshleifer/distilbart-cnn-12-6) among many others, for summarization and question-answering type tasks. However, the results were suboptimal, largely because the models weren't trained on finance-specific data. Other Hugging Face models that were pretrained on financial data either had a very small context-window, or were better suited for Sentiment Analysis based applications (which wasn't my objective). Next, I attempted to use the OpenAI API, but encountered issues with my API key, likely requiring purchasing credits. Eventually, I turned to the Google Gemini API, which yielded good results, and I didn't look back.
- <b>Tools for Text Preprocessing</b>: Text preprocessing was a labourious, involving extensive regex, BeautifulSoup, and parsing to extract required section items from filings and converting them from HTML to text format.

### Screen recording of the project
(The page takes around 3 to 4 minutes to load completely, this video has been sped up in certain places)

https://github.com/navyagarwal/corp-filings-analysis/assets/82928853/96230ea0-2674-42c1-8bad-bef63210990f



### Challenges Encountered:
- <b>Insight Extraction</b>: Extraction of useful information, especially financial metric figures and pandemic-related trends proved to be a challenge. LLMs pretrained on relevant data combined with better text pre-processing (like extraction of tabular data) would give better results. 
- <b>Computational Resource Limitations</b>: Since I was relying on free credits and compute power, processing large datasets and complex analysis was challenging due to resource constraints. The page loading time could be reduced by introducing parallel programming to make several API calls at once.
- <b>Time Constraints</b>: The time that I could dedicate to the project was constrained which impacted the quality of analysis achieved.

### Future Work
Although the current state of the project does not fully reflect the initial objectives, there is significant potential for future work in this direction. With additional resources and time, further analysis could provide valuable insights into the financial performance of these retail giants across different periods, especially in response to significant events like the COVID-19 pandemic.
