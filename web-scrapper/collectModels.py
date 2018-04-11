import json

acPhones = {}
xdaPhones = {}
gsmPhones = {}

with open("json/androidcentral-allphones.json", "r") as file:
     for phone in json.load(file):
         acPhones[phone['name'].split(' & ', 1)[0]] = phone['shortname']

with open("json/xda-all-phones.json", 'r') as file:
    for phone in json.load(file):
        xdaPhones[phone['name']] = phone['link']

with open("json/gsmarena-all-phones.json", 'r') as file:
    for phone in json.load(file):
        gsmPhones[phone['name']] = phone['link']

phones = {}
phoneLookup = {}

for phoneName, phoneLink in xdaPhones.items():
    if phoneName in acPhones and phoneName in gsmPhones:
        phones[phoneName] = {'ac': acPhones[phoneName], 'xda': phoneLink, 'gsm': gsmPhones[phoneName]}

with open('all-phones.json', 'w') as file:
    json.dump(phones, file)