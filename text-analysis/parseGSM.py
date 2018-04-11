import json, os, progressbar
import extractPhrases
from multiprocessing import Pool
from extractPhoneModels import getEntities
import pandas as pd

def parseModel(phone):
    name = phone['name']
    #tokens = name.lower().split(' ')
    link = phone['link']
    
    #if os.path.exists('results/phrases/gsm/'+link+'.csv'):
    #    return
    
    fullText = ""
    competitorModels = {}
    
    with open('../web-scrapper/json/gsm-'+link+'.json', 'r') as file:
        posts = json.load(file)
    bar = progressbar.ProgressBar(max_value=len(posts))
    counter=0
    for post in posts:
        fullText += post['text'] + ". "
        brands, models = getEntities(post['text'])
        for model in models:
            if model != name:
                if model not in competitorModels:
                    competitorModels[model] = 1
                else:
                    competitorModels[model] += 1
        counter+=1
        bar.update(counter)
    
    try:
        competitorModelsDf = pd.DataFrame.from_dict(competitorModels, orient="index").sort_values(0, ascending=False)
        competitorModelsDf.columns = ["count"]
        competitorModelsDf["percent"] = competitorModelsDf["count"] / len(posts)*100
        competitorModelsDf.to_json("results/gsm/"+link+"_competitor_models.json")
    except Exception as e:
        print(e)
        pass
    
    #df = extractPhrases.extract(fullText, tokens)
    #if df is not None:
    #    df.to_csv('results/phrases/gsm/'+link+'.csv')

if __name__ == '__main__':
    # Read in the phone models
    phones = []
    with open('../web-scrapper/all-phones.json', 'r') as file:
        for phone, value in json.load(file).items():
            phones.append({'name': phone, 'link': value['gsm'].replace('.php', '')})
    with Pool(7) as p:
        p.map(parseModel, phones)