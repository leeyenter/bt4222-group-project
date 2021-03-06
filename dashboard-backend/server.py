from flask import Flask, jsonify, request
import json, os
from socialMediaPredictions import predictImpact
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

with open('../web-scrapper/all-phones.json', 'r') as file:
    phones = json.load(file)

with open('../text-analysis/results/reddit-competitors.json', 'r') as file:
    redditCompetitors = json.load(file)

print("Loading and parsing files")
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
    if link is None:
        return []
    fp = '../text-analysis/results/'+source+'/' + link + '_interest.json'
    if not os.path.exists(fp):
#        print('Cannot find', fp)
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
#        print('Cannot find', fp)
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
    if link is None:
        return []
    fp = '../text-analysis/results/phrases/'+source+'-json/' + link + '_' + category + '.json'
    if not os.path.exists(fp):
#        print('Cannot find', fp)
        return []
    result = []
    with open(fp, 'r') as file:
        for phrase in json.load(file):
            phrase['type'] = source
            iqr = 1.5*(phrase['sentiments'][3] - phrase['sentiments'][1])
            phrase['sentiments'][0] = round(phrase['sentiments'][1] - iqr, 3)
            phrase['sentiments'][4] = round(phrase['sentiments'][3] + iqr, 3)
            result.append(phrase)
    return result

def loadCompetitors(source, link):
    if link is None:
        return []
    fp = '../text-analysis/results/'+source+'/'+link+'_competitor_models.json'
    if not os.path.exists(fp):
#        print('Cannot find', fp)
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
brandsDict = {}

with open('../text-analysis/results/reddit-competitors.json', 'r') as file:
    redditCompetitors = json.load(file)

counter = 0
for model in phones:
    counter += 1
    if counter%50 == 0:
        print(round(counter*100/len(phones), 2), "% done")
    links = phones[model]
    response = []
    response += loadPopularity('androidcentral', links['ac'])
    response += loadPopularity('gsm', links['gsm'])
    response += loadPopularity('xda', links['xda'])
    response = sorted(response, key=lambda x: x['date'])
    
    if len(response) == 0:
        continue
    
    startDate = datetime.strptime(response[0]['date'], '%Y-%m-%d')
    endDate = datetime.strptime(response[len(response)-1]['date'], '%Y-%m-%d')
    
    response += loadSocialMediaPopularity('facebook', modelLookup[model], ['comments', 'likes', 'num_posts', 'shares'])
    response += loadSocialMediaPopularity('twitter', modelLookup[model], ['num_posts', 'favourite_count', 'retweet_count'])
    response += loadSocialMediaPopularity('instagram', modelLookup[model], ['num_posts', 'comments', 'likes'])
    
    posts = {}
    sentiments = {}
    
    i = startDate
    while i <= endDate:
        posts[i.strftime('%Y-%m-%d')] = {'androidcentral': 0, 'gsm': 0, 'xda': 0, 'facebook': 0, 'twitter': 0, 'instagram': 0}
        sentiments[i.strftime('%Y-%m-%d')] = {'androidcentral': None, 'gsm': None, 'xda': None}
        i += timedelta(1)
    
    for item in response:
        if item['date'] in posts:
        #posts[item['date']] = {'androidcentral': 0, 'gsm': 0, 'xda': 0, 'facebook': 0, 'twitter': 0, 'instagram': 0}
            posts[item['date']][item['type']] = item['num_posts']
    
    for item in response:
        if 'sentiment' not in item:
            continue
            #sentiments[item['date']] = {'androidcentral': None, 'gsm': None, 'xda': None}
        if item['date'] in sentiments:
            sentiments[item['date']][item['type']] = item['sentiment']
    
    postsCombined = []
    sentimentsCombined = []
    
    for date, value in posts.items():
        value['date'] = date
        postsCombined.append(value)
    for date, value in sentiments.items():
        value['date'] = date
        sentimentsCombined.append(value)
    
    popularityDict[model] = {'num_posts': postsCombined, 'sentiments': sentimentsCombined}

    phrases = []
    phrases += fetchPhrases('androidcentral', links['ac'], 'best')
    phrases += fetchPhrases('gsm', links['gsm'], 'best')
    phrases += fetchPhrases('xda', links['xda'], 'best')
    strengthsDict[model] = phrases

    phrases = []
    phrases += fetchPhrases('androidcentral', links['ac'], 'worst')
    phrases += fetchPhrases('gsm', links['gsm'], 'worst')
    phrases += fetchPhrases('xda', links['xda'], 'worst')
    weaknessesDict[model] = phrases

    competitors = []
    competitors += loadCompetitors('androidcentral', links['ac'])
    competitors += loadCompetitors('gsm', links['gsm'])
    competitors += loadCompetitors('xda', links['xda'])
    
    try:
        for comp, count in redditCompetitors[model].items():
            competitors.append({'competitor': comp, 'count': count, 'type': 'reddit'})
    except:
        pass
    
    cDict = {}
    bDict = {}
    for competitor in competitors:
        if competitor['competitor'] not in cDict:
            cDict[competitor['competitor']] = {'androidcentral': 0, 'xda': 0, 'gsm': 0, 'reddit': 0, 'total': 0}
        cDict[competitor['competitor']][competitor['type']] = competitor['count']
        brand = competitor['competitor'].split(' ', 1)[0]
        if brand not in bDict:
            bDict[brand] = 1
        else:
            bDict[brand] += 1
    
    competitors = []
    key = 1
    for competitor, value in cDict.items():
        value['model'] = competitor
        value['total'] = value['gsm'] + value['reddit'] + value['androidcentral'] + value['xda']
        value['key'] = key
        competitors.append(value)
        key += 1
    brands = []
    key = 1
    for brand, count in bDict.items():
        brands.append({'brand': brand, 'count': count, 'key': key})
        key += 1
    
    competitorsDict[model] = [x for x in sorted(competitors, key=lambda x: x['total'], reverse = True) if x['total'] > 5]
    brandsDict[model] = [x for x in sorted(brands, key=lambda x: x['count'], reverse = True) if x['count'] > 5]


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

@app.route("/brands/<model>/")
def fetchBrands(model):
    return jsonify(brandsDict[model])

@app.route('/predict/', methods=['POST'])
def fetchPredictions():
    body = request.get_json()
    if 'brand' not in body or 'caption' not in body:
        return jsonify({'ok': False, 'error': 'Malformed body'})
    elif body['brand'] not in brandLookup:
        return jsonify({'ok': False, 'error': 'Brand not found'})
    else:
        return jsonify(predictImpact(body['caption'], body['brand']))

if __name__ == '__main__':
    app.run(debug = False, port = 5132)