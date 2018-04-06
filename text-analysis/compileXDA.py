import os, json
filenames = os.listdir("results/xda")

phones = {}
with open("../web-scrapper/json/xda-all-phones.json", "r") as file:
    for phone in json.load(file):
        phones[phone['link']] = phone['name']

results = {}

for filename in filenames:
    name, tag = filename.replace(".json", "").split("_", 1)
    model = phones[name]
    brand = model.split(" ", 1)[0]
    if brand in results:
        with open("results/xda/"+filename, "r") as file:
            results[brand][tag][model] = json.load(file)
    else:
        results[brand] = {'interest': {}, 'competitor_brands': {}, 'competitor_models': {}, 'categories': {}}

for brand, obj in results.items():
    with open("results/compiled/xda-"+brand+".json", "w") as file:
        json.dump(obj, file)