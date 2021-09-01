import requests
import time

url = "https://covid-19-data.p.rapidapi.com/country"

headers = {
    'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
    }

querystring = {"name":"russia"}

output = open("api_output.txt", "w")

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
output.write(response.text+"\n")

#{"message":"Invalid API key. Go to https:\/\/docs.rapidapi.com\/docs\/keys for more info."}

headers['x-rapidapi-key'] = "c23e630163msh72ca7e9d304a4adp1f32b5jsn864c31e7f979"

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
output.write(response.text+"\n")

#[{"country":"Russia","code":"RU","confirmed":10633869,"recovered":8810973,"critical":2300,"deaths":195255,"latitude":61.52401,"longitude":105.318756,"lastChange":"2021-03-12T20:14:56+01:00","lastUpdate":"2021-09-01T12:30:03+02:00"}]

time.sleep(1)

url = "https://covid-19-data.p.rapidapi.com/report/totals"

querystring = {"date":"2020-07-21"}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
output.write(response.text)

# [{"confirmed":15085083,"recovered":9105030,"deaths":618504,"active":5361549,"critical":63786,"date":"2020-07-21"}]

output.close()