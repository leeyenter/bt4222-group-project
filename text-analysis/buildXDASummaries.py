import json, re, os
from textblob import TextBlob
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from extractPhoneModels import getEntities
from multiprocessing import Pool

def makeSummary(phone):
    phoneName = phone[0]
    phoneURL = phone[1]
    
#    if os.path.exists("results/xda/"+phoneURL+"_categories.json"):
#        return
        
    phoneBrand = phoneName.split(" ", 1)[0]
    with open('../web-scrapper/json/xda-'+phoneURL+'.json', 'r') as file:
        res = json.load(file)
    
    def solve(s):                                             
        return re.sub(r'(\d)(st|nd|rd|th)', r'\1', s)
        
    postCount = {}
    sentiments = {}
    
    categories = []
    
    startDate = None
    endDate = None
    
    competitorBrands = {}
    competitorModels = {}
    
    if len(res) == 0:
        return
    
    for category in res:
        brands = {}
        models = {}
        categorySentiments = []
        
        for post in category['threads']:
            tb = TextBlob(post['text'])
            brandsFound, modelsFound = getEntities(post['text'])
            
            for brand in brandsFound:
                if brand != phoneBrand:
                    if brand in competitorBrands:
                        competitorBrands[brand] += 1
                    else:
                        competitorBrands[brand] = 1
                    
                    if brand in brands:
                        brands[brand] += 1
                    else:
                        brands[brand] = 1
                        
            for model in modelsFound:
                if model != phoneName:
                    if model in competitorModels:
                        competitorModels[model] += 1
                    else:
                        competitorModels[model] = 1
                    
                    if model in models:
                        models[model] += 1
                    else:
                        models[model] = 1
            
            categorySentiments.append(tb.sentiment.polarity)
            timestamp = datetime.strptime(solve(post['time']), "%d %B %Y, %I:%M %p").date()
            if timestamp in postCount:
                postCount[timestamp] += 1
                sentiments[timestamp].append(tb.sentiment.polarity)
            else:
                postCount[timestamp] = 1
                sentiments[timestamp] = [tb.sentiment.polarity]
                
            if startDate is None or timestamp < startDate:
                startDate = timestamp
            if endDate is None or timestamp > endDate:
                endDate = timestamp
        
        catSentiments = None
        if len(categorySentiments) > 0:
            catSentiments = list(np.percentile(categorySentiments, [25, 50, 75]))
            
        categories.append({
                "title": category['title'], 
                "rating": category['rating'], 
                "num_posts": len(categorySentiments), 
                "sentiments": catSentiments, 
                "competitor_brands": brands, 
                "competitor_models": models
        })
                
    dateArr = []
    countsArr = []
    sentimentsArr = []
    
    if startDate is None:
        return
    
    currDate = startDate
    while currDate <= endDate:
        dateArr.append(datetime.strftime(currDate, "%Y-%m-%d"))
        if currDate in postCount:
            countsArr.append(postCount[currDate])
            sentimentsArr.append(np.percentile(sentiments[currDate], [25, 50, 75]))
        else:
            countsArr.append(0)
            sentimentsArr.append(None)
        currDate += timedelta(1)
    
    df = pd.DataFrame({"date": dateArr, "num_posts": countsArr, "sentiments": sentimentsArr})
    df = df.set_index("date")
    df.to_json("results/xda/"+phoneURL+"_interest.json")
    
    with open("results/xda/"+phoneURL+"_categories.json", "w") as file:
        json.dump({"categories": categories}, file)
        
    try:
        competitorBrandsDf = pd.DataFrame.from_dict(competitorBrands, orient="index").sort_values(0, ascending=False)
        competitorBrandsDf.columns = ["count"]
        competitorBrandsDf["percent"] = competitorBrandsDf['count'] / df["num_posts"].sum()*100
        competitorBrandsDf.to_json("results/xda/"+phoneURL+"_competitor_brands.json")
    except:
        pass
    
    try:
        competitorModelsDf = pd.DataFrame.from_dict(competitorModels, orient="index").sort_values(0, ascending=False)
        competitorModelsDf.columns = ["count"]
        competitorModelsDf["percent"] = competitorModelsDf['count'] / df["num_posts"].sum()*100
        competitorModelsDf.to_json("results/xda/"+phoneURL+"_competitor_models.json")
    except Exception as e:
        print(e)
        pass
    


if __name__ == "__main__":
    phones = []
    with open("../web-scrapper/json/xda-all-phones.json", "r") as file:
        for phone in json.load(file):
            phones.append((phone["name"], phone["link"]))
    
    with Pool(7) as p:
        p.map(makeSummary, phones)