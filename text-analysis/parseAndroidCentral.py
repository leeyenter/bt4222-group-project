from extractPhoneModels import getEntities
import json, re
from datetime import datetime, timedelta
from textblob import TextBlob
from extractPhrases import extract

res = []
phoneName = "Samsung Galaxy S9 & S9+"
nameTokens = phoneName.lower().split(" ")
phoneBrand = phoneName.split(" ", 1)[0].strip()
phones = {}

with open("../web-scrapper/json/androidcentral-allphones.json", "r") as file:
    for phone in json.load(file):
        phones[phone["name"]] = phone["shortname"]

with open("../web-scrapper/json/androidcentral-"+phones[phoneName]+".json") as file:
    for line in file:
        res += json.loads(line)

startDate = None
endDate = None
counts = {}
competitorModels = {}
competitorBrands = {}
sentiments = []

phrases = []
fullText = ""

def parseTime(timeStr):
    return datetime.strptime(timeStr, "%m-%d-%Y %I:%M %p")

def getDate(timeObj):
    return datetime.strftime(timeObj, "%Y-%m-%d")

def incrementDateCount(timeObj):
    global startDate
    global endDate
    global counts
    
    if startDate is None or timeObj < startDate:
        startDate = timeObj
    if endDate is None or timeObj > endDate:
        endDate = timeObj
    dateStr = getDate(timeObj)
    if dateStr in counts:
        counts[dateStr] += 1
    else:
        counts[dateStr] = 1

def parseThread(thread):
    global startDate, endDate, competitorBrands, competitorModels, sentiments, phrases, fullText
    
    for post in thread:
        brands, models = getEntities(post['text'])
        fullText += post['text'] + ". "
#        for sentence in post['text'].split("."):
#            if sentence.count(" ") > 2:
#                phrases += extract(sentence, nameTokens)
        sentiments.append(TextBlob(post['text']).sentiment.polarity)
        for brand in brands:
            if brand != phoneBrand:
                if brand not in competitorBrands:
                    competitorBrands[brand] = 1
                else:
                    competitorBrands[brand] += 1
        for model in models:
            if model != phoneName:
                if model not in competitorModels:
                    competitorModels[model] = 1
                else:
                    competitorModels[model] += 1
        incrementDateCount(parseTime(post['time']))
        parseThread(post['replies'])
        
count = 0
for thread in res:
    parseThread(thread['thread'])
    count += 1
    if count % 2 == 0:
        print(str(round(count*100/len(res), 2)) + "% done")

i = startDate
dateArr = []
countArr = []
while i <= endDate:
    dateArr.append(i)
    iStr = getDate(i)
    if iStr in counts:
        countArr.append(counts[iStr]+1)
    else:
        countArr.append(1)
    i += timedelta(1)

import pandas as pd
df = pd.DataFrame({"date": dateArr, "No. of posts": countArr})
df = df.set_index("date")
df.head()

import matplotlib.pyplot as plt
#df.plot(title=phoneName, logy = True)

competitorBrandsDf = pd.DataFrame.from_dict(competitorBrands, orient="index").sort_values(0, ascending=False)
competitorModelsDf = pd.DataFrame.from_dict(competitorModels, orient="index").sort_values(0, ascending=False)
competitorBrandsDf.columns = ["Count"]
competitorModelsDf.columns = ["Count"]
competitorBrandsDf["Percent"] = competitorBrandsDf.Count / df["No. of posts"].sum()*100
competitorModelsDf["Percent"] = competitorModelsDf.Count / df["No. of posts"].sum()*100

print(" == BRANDS == ")
print(competitorBrandsDf.head())
print(" == MODELS == ")
print(competitorModelsDf.head())

phrases = {}
sentences = [ x for x in re.split(r"[,?!.]+", fullText) if x.count(" ") > 2]
count = 0
for sentence in sentences:
    for result in extract(sentence, nameTokens):
        if result['phrase'] in phrases:
            phrases[result['phrase']].append(result['sentiment'])
        else:
            phrases[result['phrase']] = [result['sentiment']]
    count += 1
    if count % 200 == 0:
        print(str(round(count*100/len(sentences), 2)) + "% done")

phraseCount = {}
for phrase, sentiments in phrases.items():
    if len(sentiments) > 5:
        phraseCount[phrase] = len(sentiments)
    
plt.hist(sentiments, bins=50)
