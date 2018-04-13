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
brands = set()

for phoneName, phoneLink in xdaPhones.items():
    if phoneName not in phones:
        phones[phoneName] = {'ac': None, 'xda': None, 'gsm': None}
    phones[phoneName]['xda'] = phoneLink
    
for phoneName, phoneLink in acPhones.items():
    if phoneName not in phones:
        phones[phoneName] = {'ac': None, 'xda': None, 'gsm': None}
    phones[phoneName]['ac'] = phoneLink
    
for phoneName, phoneLink in gsmPhones.items():
    if phoneName not in phones:
        phones[phoneName] = {'ac': None, 'xda': None, 'gsm': None}
    phones[phoneName]['gsm'] = phoneLink.replace('.php', '')

oldPhones = phones.copy()
for name, value in oldPhones.items():
    count = 0
    if value['gsm'] is not None:
        count += 1
    if value['xda'] is not None:
        count += 1
    if value['gsm'] is not None:
        count += 1
    if count <= 2:
        phones.pop(name)
    else:
        brands.add(name.split(' ', 1)[0])

#    if phoneName in acPhones and phoneName in gsmPhones:
#        phones[phoneName] = {'ac': acPhones[phoneName], 'xda': phoneLink, 'gsm': gsmPhones[phoneName]}

with open('all-phones.json', 'w') as file:
    json.dump(phones, file)

with open('brands.json', 'w') as file:
    json.dump(list(brands), file)