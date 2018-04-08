import json, os
import extractPhrases
from multiprocessing import Pool

def parseThread(thread):
    returnText = ''
    for post in thread:
        returnText += post['text'] + '. ' + parseThread(post['replies']) + '. '
    return returnText

def parsePhrases(phone):
    phoneName = phone[0]
    phoneLink = phone[1]
    tokens = phoneName.lower().split(' ')
    
    if os.path.exists('results/phrases/androidcentral/'+phoneLink+'_best.json'):
        return
    
    fullText = ""
    try:
        with open('../web-scrapper/json/androidcentral-'+phoneLink+'.json', 'r') as file:
            for line in file:
                for thread in json.loads(line):
                    fullText += parseThread(thread['thread']) + '. '
    except Exception as e:
        print(e)
        return
    df = extractPhrases.extract(fullText, tokens)
    if df is not None:
        best, worst = extractPhrases.getTopPhrases(df)
        best.to_json('results/phrases/androidcentral/' + phoneLink + '_best.json', orient='index')
        worst.to_json('results/phrases/androidcentral/' + phoneLink + '_worst.json', orient='index')

if __name__ == '__main__':
    phones = []
    with open("../web-scrapper/json/androidcentral-allphones.json", "r") as file:
        for phone in json.load(file):
            phones.append((phone["name"], phone["shortname"]))
    
    with Pool(12) as p:
        p.map(parsePhrases, phones)