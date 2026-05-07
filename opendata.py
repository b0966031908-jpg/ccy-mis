import requests, json
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName=臺中市"
headers = {'User-Agent' : 'Mozilla/5.0'}
Data = requests.get(url)
#print(Data.text)

JsonData = json.loads(Data.text)
print(JsonData["records"]["location"][0]["locationName"],"最新天氣預報")

Weather = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
Rain = json.loads(Data.text)["records"]["location"][0]["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
print(Weather + "，降雨機率：" + Rain + "%")
