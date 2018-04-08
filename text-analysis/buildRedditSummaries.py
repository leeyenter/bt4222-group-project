from extractPhoneModels import getEntities
import json
from datetime import datetime, timezone
import progressbar

def parseTime(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc)

files = []

with open("../web-scrapper/json/reddit-Smartphones.json", "r") as file:
    files.append(json.load(file))

with open("../web-scrapper/json/reddit-PickAnAndroidForMe.json", "r") as file:
    files.append(json.load(file))
    
with open("../web-scrapper/json/reddit-PickMeAPhone.json", "r") as file:
    files.append(json.load(file))
    
with open("../web-scrapper/json/reddit-phones.json", "r") as file:
    files.append(json.load(file))
    
res = {}
for file in files:
    for key, value in file.items():
        if key in res:
            print("key in res")
        res[key] = value

competitors = {}

def getCompetitors(thread, prevBrands, prevModels):
    postText = ""
    if 'title' in thread:
        postText = thread['title'] + ' '
    postText += thread['text']
    foundBrands, foundModels = getEntities(postText)
    
    brands = prevBrands.copy()
    models = prevModels.copy()
    brands.update(foundBrands)
    models.update(foundModels)
    
    for model in models:
        # For each model listed, we want to take note 
        # which other models are mentioned with this model
        if model not in competitors:
            competitors[model] = {}
        for competingModel in models:
            if competingModel == model:
                continue
            if competingModel in competitors[model]:
                competitors[model][competingModel] += 1
            else:
                competitors[model][competingModel] = 1
    
    for reply in thread['replies']:
        getCompetitors(reply, brands, models)
        
bar = progressbar.ProgressBar(max_value = len(res))

counter = 0
for key, thread in res.items():
    getCompetitors(thread, set(), set())
    counter += 1
    bar.update(counter)

with open("results/reddit-competitors.json", "w") as file:
    json.dump(competitors, file)
    