from extractPhoneModels import getEntities
import json, progressbar, os
from datetime import datetime, timedelta
from textblob import TextBlob
import numpy as np
from multiprocessing import Pool

def parseTime(timeStr):
    return datetime.strptime(timeStr, "%m-%d-%Y %I:%M %p")

def getDate(timeObj):
    return datetime.strftime(timeObj, "%Y-%m-%d")

def makeSummary(phone):
    phoneName = phone[0]
    phoneURL = phone[1]
    
    if os.path.exists("results/androidcentral/"+phoneURL+"_interest.json"):
        return
    
    phoneBrand = phoneName.split(" ", 1)[0].strip()
    
    res = []
    
    try:
        with open("../web-scrapper/json/androidcentral-"+phoneURL+".json") as file:
            for line in file:
                res += json.loads(line)
    except:
        print(phoneName, "(", phoneURL, ") not found")
        return
    
    startEndDates = [None, None]
    counts = {}
    competitorModels = {}
    competitorBrands = {}
    sentiments = {}
    
    def parseThread(thread, startEndDates):
        for post in thread:
            brands, models = getEntities(post['text'])
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
                        
            timeObj = parseTime(post['time'])
            
            if startEndDates[0] is None or timeObj < startEndDates[0]:
                startEndDates[0] = timeObj
            if startEndDates[1] is None or timeObj > startEndDates[1]:
                startEndDates[1] = timeObj
                
            dateStr = getDate(timeObj)
            if dateStr in counts:
                sentiments[dateStr].append(TextBlob(post['text']).sentiment.polarity)
                counts[dateStr] += 1
            else:
                counts[dateStr] = 1
                sentiments[dateStr] = [TextBlob(post['text']).sentiment.polarity]
                
            parseThread(post['replies'], startEndDates)
            
#    bar = progressbar.ProgressBar(max_value = len(res))
#    count = 0
    for thread in res:
        parseThread(thread['thread'], startEndDates)
#        count += 1
#        bar.update(count)
    
    if startEndDates[0] is None:
        return
    
    i = startEndDates[0]
    dateArr = []
    countArr = []
    sentimentsArr = []
    while i <= startEndDates[1]:
        dateArr.append(datetime.strftime(i, "%Y-%m-%d"))
        iStr = getDate(i)
        if iStr in counts:
            countArr.append(counts[iStr])
            sentimentsArr.append(np.percentile(sentiments[iStr], [25, 50, 75]))
        else:
            countArr.append(0)
            sentimentsArr.append(None)
        i += timedelta(1)
    
    import pandas as pd
    df = pd.DataFrame({"date": dateArr, "num_posts": countArr, "sentiments": sentimentsArr})
    df = df.set_index("date")
    df.to_json("results/androidcentral/"+phoneURL+"_interest.json")
    
    try:
        competitorBrandsDf = pd.DataFrame.from_dict(competitorBrands, orient="index").sort_values(0, ascending=False)
        competitorBrandsDf.columns = ["count"]
        competitorBrandsDf["percent"] = competitorBrandsDf["count"] / df["num_posts"].sum()*100
        competitorBrandsDf.to_json("results/androidcentral/"+phoneURL+"_competitor_brands.json")
    except Exception as e:
        print(e)
        pass
    
    try:
        competitorModelsDf = pd.DataFrame.from_dict(competitorModels, orient="index").sort_values(0, ascending=False)
        competitorModelsDf.columns = ["count"]
        competitorModelsDf["percent"] = competitorModelsDf["count"] / df["num_posts"].sum()*100
        competitorModelsDf.to_json("results/androidcentral/"+phoneURL+"_competitor_models.json")
    except Exception as e:
        print(e)
        pass

if __name__ == "__main__":
    phones = []
    with open("../web-scrapper/json/androidcentral-allphones.json", "r") as file:
        for phone in json.load(file):
            phones.append((phone["name"], phone["shortname"]))
    
#    counter = 0
#    bar = progressbar.ProgressBar(max_value = len(phones))
#    for phone in phones:
#        makeSummary(phone)
#        counter += 1
#        bar.update(counter)
    with Pool(8) as p:
        p.map(makeSummary, phones)