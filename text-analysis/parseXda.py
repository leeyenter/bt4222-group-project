import json, re
from textblob import TextBlob
import statistics
from datetime import datetime, timedelta
import pandas as pd

from extractPhoneModels import getEntities
import extractPhrases

phones = {}
with open("../web-scrapper/json/xda-all-phones.json", "r") as file:
    for phone in json.load(file):
        phones[phone["name"]] = phone["link"]
        
phone = "Samsung Galaxy S7"
tokens = phone.lower().split(" ")
brand = phone.split(" ", 1)[0]
with open('../web-scrapper/json/xda-'+phones[phone]+'.json', 'r') as file:
    res = json.load(file)

def solve(s):                                             
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', s)
    
postCount = {}
startDate = None
endDate = None

phrases = {}

for category in res:
    print("")
    print("Title:", category['title'], "(", category['rating'], "stars )")
    sentiments = []
    brands = set()
    models = set()
    
    for post in category['threads']:
        tb = TextBlob(post['text'])
        sentiments.append(tb.sentiment.polarity)
        brandsFound, modelsFound = getEntities(post['text'])
        brands.update(brandsFound)
        models.update(modelsFound)
        phrasesFound = extractPhrases.extract(post['text'], tokens)
        for phrase in phrasesFound:
            if phrase['phrase'] in phrases:
                phrases[phrase['phrase']].append(phrase['sentiment'])
            else:
                phrases[phrase['phrase']] = [phrase['sentiment']]
        timestamp = datetime.strptime(solve(post['time']), "%d %B %Y, %I:%M %p").date()
        if timestamp in postCount:
            postCount[timestamp] += 1
        else:
            postCount[timestamp] = 1
        
        if startDate is None or timestamp < startDate:
            startDate = timestamp
        if endDate is None or timestamp > endDate:
            endDate = timestamp
        
    print(" --", len(sentiments), "posts")
    try:
        print(" -- Average sentiment of", round(statistics.median(sentiments), 2), ", stdev:", round(statistics.stdev(sentiments), 2))
    except:
        print(" -- Average sentiment of", round(statistics.median(sentiments), 2))
    if brand in brands:
        brands.remove(brand)
    if phone in models:
        models.remove(phone)
    print(" -- Competing brands: ", brands)
    print(" -- Competing models: ", models)

currDate = startDate
while currDate <= endDate:
    if currDate not in postCount:
        postCount[currDate] = 0
    currDate += timedelta(1)

countsDf = pd.DataFrame.from_dict(postCount, orient="index")
countsDf.plot()
# Maybe we can plot a barchart that shows how many posts each 

phraseStrs = list(phrases.keys())
