import os, json
filenames = os.listdir("results/androidcentral")

phones = {}
with open("../web-scrapper/json/androidcentral-allphones.json", "r") as file:
    for phone in json.load(file):
        phones[phone['shortname']] = phone['name']

results = {}

for filename in filenames:
    name, tag = filename.replace(".json", "").split("_", 1)
    model = phones[name]
    brand = model.split(" ", 1)[0]
    if brand in results:
        with open("results/androidcentral/"+filename, "r") as file:
            results[brand][tag][model] = json.load(file)
    else:
        results[brand] = {'interest': {}, 'competitor_brands': {}, 'competitor_models': {}}

for brand, obj in results.items():
    with open("results/compiled/androidcentral-"+brand+".json", "w") as file:
        json.dump(obj, file)