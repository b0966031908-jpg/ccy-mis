import requests
from bs4 import BeautifulSoup

url = "https://ccy-mis.vercel.app/cy"
Data = requests.get(url)
Data.encoding = "utf-8"
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.find("a")

for item in result:
	print(item.text)
	print()
