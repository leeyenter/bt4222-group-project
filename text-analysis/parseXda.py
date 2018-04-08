import json, os
import extractPhrases
from multiprocessing import Pool

def parsePhrases(phone):
    phoneName = phone[0]
    phoneLink = phone[1]
    tokens = phoneName.lower().split(' ')
    #brand = phoneName.split(' ', 1)[0]
    
    if os.path.exists('results/phrases/xda/'+phoneLink+'_best.json'):
        return
    
    with open('../web-scrapper/json/xda-'+phoneLink+'.json', 'r') as file:
        res = json.load(file)
    
    fullText = ""
    total = 0
    for category in res:
        total += len(category['threads'])
    
    for category in res:
        for post in category['threads']:
            fullText += post['text'].lower() + '. '
    
    df = extractPhrases.extract(fullText, tokens)
    if df is not None:
        best, worst = extractPhrases.getTopPhrases(df)
        best.to_json('results/phrases/xda/' + phoneLink + '_best.json', orient='index')
        worst.to_json('results/phrases/xda/' + phoneLink + '_worst.json', orient='index')

if __name__ == '__main__':
    phones = []
    with open("../web-scrapper/json/xda-all-phones.json", "r") as file:
        for phone in json.load(file):
            phones.append((phone["name"], phone["link"]))
        
    with Pool(7) as p:
        p.map(parsePhrases, phones)