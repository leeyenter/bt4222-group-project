from extractPhoneModels import getEntities
import json
from datetime import datetime, timezone, timedelta

files = []

with open("json/reddit-Smartphones.json", "r") as file:
    files.append(json.load(file))

with open("json/reddit-PickAnAndroidForMe.json", "r") as file:
    files.append(json.load(file))
    
with open("json/reddit-PickMeAPhone.json", "r") as file:
    files.append(json.load(file))
    
with open("json/reddit-phones.json", "r") as file:
    files.append(json.load(file))

res = {}
for file in files:
    for key, value in file.items():
        if key in res:
            print("key in res")
        res[key] = value

with open("json/xda-all-phones.json", "r") as file:
    phoneJson = json.load(file)

def parseTime(seconds):
#    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(seconds))
#    return time.strftime("%Y-%m-%d", time.gmtime(seconds))
    return datetime.fromtimestamp(seconds, timezone.utc)


def getDate(timeObj):
    return datetime.strftime(timeObj, "%Y-%m-%d")

counts = {}
startDate = None
endDate = None

modelCounts = {}

def incrementDateCount(timeObj, model):
    global startDate
    global endDate
    global counts
    
    if model not in counts:
        counts[model] = {}
    
    if startDate is None or timeObj < startDate:
        startDate = timeObj
    if endDate is None or timeObj > endDate:
        endDate = timeObj
    dateStr = getDate(timeObj)
    if dateStr in counts[model]:
        counts[model][dateStr] += 1
    else:
        counts[model][dateStr] = 1

def doCount(threadObj):
    global modelCounts 
    
    text = threadObj['text']
    if "title" in threadObj:
        text += " " + threadObj["title"]
    brands, models = getEntities(text.lower())
    for model in models:
        if model in modelCounts:
            modelCounts[model] += 1
        else:
            modelCounts[model] = 1
        incrementDateCount(parseTime(threadObj['created']), model)
    for reply in threadObj['replies']:
        doCount(reply)

for key, thread in res.items():
    doCount(thread)

# Now let's try plot a graph?
import pandas as pd
import matplotlib.pyplot as plt

modelCountsDf = pd.DataFrame.from_dict(modelCounts, orient="index")
modelCountsDf.columns = ["NumPosts"]
modelCountsDf.sort_values("NumPosts", ascending=False, inplace=True)
modelCountsDf.plot.bar()

countsDfDict = {}
for model in modelCounts.keys():
    countsDfDict[model] = []
i = startDate
while i <= endDate:
    dateStr = datetime.strftime(i, "%Y-%m-%d")
    for model in modelCounts.keys():
        if dateStr in counts[model]:
            countsDfDict[model].append(counts[model][dateStr])
        else:
            countsDfDict[model].append(0)
    i += timedelta(1)

countsDf = pd.DataFrame(countsDfDict, index=pd.date_range(datetime.strftime(startDate, "%Y-%m-%d"), periods = 1 + (endDate - startDate).days))
countsDf.plot()
