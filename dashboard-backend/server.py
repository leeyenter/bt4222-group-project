from flask import Flask, jsonify
import json, os

app = Flask(__name__)
with open('../web-scrapper/all-phones.json', 'r') as file:
    phones = json.load(file)

with open('../text-analysis/results/reddit-competitors.json', 'r') as file:
    redditCompetitors = json.load(file)

brandLookup = {}
modelLookup = {}
for phone in phones:
    brand = phone.split(' ', 1)[0]
    if brand in brandLookup:
        brandLookup[brand].append(phone)
    else:
        brandLookup[brand] = [phone]
    modelLookup[phone] = brand

def loadPopularity(source, link):
    fp = '../text-analysis/results/'+source+'/' + link + '_interest.json'
    if not os.path.exists(fp):
        print('Cannot find', fp)
        return []
    with open(fp, 'r') as file:
        overview = json.load(file)
    response = []
    for date in overview['num_posts'].keys():
        response.append({'date': date, 'num_posts': overview['num_posts'][date], 'sentiment': overview['sentiments'][date], 'type': source})
    return response

def loadSocialMediaPopularity(source, brand, keys):
    fp = source+'-by-brand.json'
    if not os.path.exists(fp):
        print('Cannot find', fp)
        return []
    with open(fp, 'r') as file:
        try:
            overview = json.load(file)[brand]
        except:
            return []
    response = []
    for date in overview.keys():
        obj = {'date': date, 'type': source}
        for key in keys:
            obj[key] = overview[date][key]
        response.append(obj)
    return response

def fetchPhrases(source, link, category):
    result = []
    fp = '../text-analysis/results/phrases/'+source+'-json/' + link + '_' + category + '.json'
    if not os.path.exists(fp):
        print('Cannot find', fp)
        return result
    with open(fp, 'r') as file:
        for phrase in json.load(file):
            phrase['type'] = source
            iqr = 1.5*(phrase['sentiments'][3] - phrase['sentiments'][1])
            phrase['sentiments'][0] = round(phrase['sentiments'][1] - iqr, 3)
            phrase['sentiments'][4] = round(phrase['sentiments'][3] + iqr, 3)
            result.append(phrase)
    return result

def loadCompetitors(source, link):
    fp = '../text-analysis/results/'+source+'/'+link+'_competitor_models.json'
    if not os.path.exists(fp):
        print('Cannot find', fp)
        return []
    result = []
    with open(fp, 'r') as file:
        res = json.load(file)
        if 'count' not in res:
            print('Failed for', fp)
            return []
        for phone in res['count'].keys():
            result.append({'competitor': phone, 'count': res['count'][phone], 'percent': res['percent'][phone], 'type': source})
    return result

popularityDict = {}
strengthsDict = {}
weaknessesDict = {}
competitorsDict = {}

for model in phones:
    links = phones[model]
    response = []
    response += loadPopularity('androidcentral', links['ac'])
    response += loadPopularity('gsm', links['gsm'].replace('.php', ''))
    response += loadPopularity('xda', links['xda'])
    response += loadSocialMediaPopularity('facebook', modelLookup[model], ['comments', 'likes', 'num_posts', 'shares'])
    response += loadSocialMediaPopularity('twitter', modelLookup[model], ['num_posts', 'favourite_count', 'retweet_count'])
    response += loadSocialMediaPopularity('instagram', modelLookup[model], ['num_posts', 'comments', 'likes'])
    popularityDict[model] = response

    phrases = []
    phrases += fetchPhrases('androidcentral', links['ac'], 'best')
    phrases += fetchPhrases('gsm', links['gsm'].replace('.php', ''), 'best')
    phrases += fetchPhrases('xda', links['xda'], 'best')
    strengthsDict[model] = phrases

    phrases = []
    phrases += fetchPhrases('androidcentral', links['ac'], 'worst')
    phrases += fetchPhrases('gsm', links['gsm'].replace('.php', ''), 'worst')
    phrases += fetchPhrases('xda', links['xda'], 'worst')
    weaknessesDict[model] = phrases
    
    competitors = []
    competitors += loadCompetitors('androidcentral', links['ac'])
    competitors += loadCompetitors('gsm', links['gsm'].replace('.php', ''))
    competitors += loadCompetitors('xda', links['xda'])
    competitorsDict[model] = competitors

@app.route("/model/<brand>/")
def fetchModels(brand):
    return jsonify(brandLookup[brand])

@app.route("/sentiment-post/<model>/")
def fetchPopularity(model):
    # TODO: To pull social media stuff also
    return jsonify(popularityDict[model])

@app.route("/strengths/<model>/")
def fetchStrengths(model):
    return jsonify(strengthsDict[model])

@app.route("/weaknesses/<model>/")
def fetchWeaknesses(model):
    return jsonify(weaknessesDict[model])

@app.route("/competitors/<model>/")
def fetchCompetitors(model):
    return jsonify(competitorsDict[model])

if __name__ == '__main__':
    app.run(debug = True, port = 5132)