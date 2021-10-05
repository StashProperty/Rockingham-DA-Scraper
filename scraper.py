import datetime
from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
import pandas as pd
import unicodedata

DATABASE = "data.sqlite"
DATA_TABLE = "data"
engine = create_engine(f'sqlite:///{DATABASE}', echo=False)

da_set = []
headers={"User-Agent":"PostmanRuntime/7.28.3"}
base_url = "https://www.rockingham.wa.gov.au"
today = datetime.datetime.strftime(datetime.datetime.now(),"%m-%d-%Y")

raw = requests.get("https://rockingham.wa.gov.au/planning-and-building/local-planning/town-planning-advertising-and-submissions",headers=headers)
soup = BeautifulSoup(raw.content, 'html.parser')
links = soup.find_all('a',class_ = 'hotbox')


for item in links:
	if "Submissions close" in item.text:
		next_page = requests.get(base_url+item.attrs['href'], headers=headers)
		next_soup = BeautifulSoup(next_page.content, 'html.parser')
		description_parent = next_soup.find(class_ = 'step-up')
		raw_description = []
		for tag in description_parent.find_all("p"):
			raw_description.append(unicodedata.normalize('NFKD',tag.text))
		description = " ".join(raw_description)

		related_documents = next_soup.find("div",class_='related-documents-wrap').find_all("a")
		for link in related_documents:
			if "development-application" in link.attrs['href']:
				info_url = base_url + link.attrs['href']
				address = link.text.replace("Development application - ","")
		da = {}
		da['council_reference'] = 0
		da['description'] = description
		da['info_url'] = info_url
		da['date_scraped'] = today
		da['address'] = address
		da_set.append(da)

data = pd.DataFrame(da_set)
data.to_sql(DATA_TABLE, con=engine, if_exists='append',index=False)
