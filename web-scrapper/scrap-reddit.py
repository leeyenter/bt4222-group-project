import requests, json, time
from multiprocessing import Pool

def fetchComments(children):
    results = []
    for child in children:
        try:
            text = child['data']['body']
            if text == "[removed]" or text == "Sorry, your submission has been automatically removed. Due to high quantities of spam, users with less than 10 karma are restricted from posting. If you would like to request an exception, please message the moderators.\n\n*I am a bot, and this action was performed automatically. Please [contact the moderators of this subreddit](/message/compose/?to=/r/phones) if you have any questions or concerns.*":
                text = ""
            created = child['data']['created_utc']
            if len(child['data']['replies']) > 0:
                replies = fetchComments(child['data']['replies']['data']['children'])
            else:
                replies = []
            results.append({'text': text, 'created': created, 'replies': replies})
        except:
            print(child)
    return results

def get(url, params):
    headers = {'User-agent': 'yenter-phone-comments-0.1'}
    r = requests.get(url, 
                     headers = headers, 
                     params = params, 
                     timeout = 5)
    return r
    #return get(url, params)

def fetchLinks(sub, results, after):
    params = {}
    if after is not None:
        params["after"] = after
    r = get("https://www.reddit.com/r/"+sub+"/hot/.json", params)
    j = r.json()
    
    children = j['data']['children']
    
    counter = 0
    
    for child in children:
        counter+=1 
        if not child['data']['stickied']:
            title = child["data"]["title"]
            text = child['data']['selftext']
            created = child["data"]["created_utc"]
            # get the timestamp as well
    #        name = child['data']['name']
            commentsR = get("https://www.reddit.com/r/"+sub+"/comments/"+child['data']['id']+"/.json", {})
            commentsJ = commentsR.json()
            comments = fetchComments(commentsJ[1]['data']['children'])
            results[child['data']['id']] = {
                    "title": title, 
                    "text": text, 
                    "created": created, 
                    "replies": comments}
        print(str(round(counter*100/len(children), 2))+"% done")
    after = j['data']['after']
    return after

def scrapSub(sub):
    try:
        with open('json/reddit-'+sub+'.json', 'r') as file:
            results = json.load(file)
    except:
        results = {}
    
    after = fetchLinks(sub, results, None)
    for i in range(10):
        print("Sleeping..")
        time.sleep(30) # in case of any rate limitation
        print("== Page", i+2, "==")
        print(after)
        after = fetchLinks(sub, results, after)
        with open('json/reddit-'+sub+'.json', 'w') as file:
            json.dump(results, file)

if __name__ == "__main__":
    subs = ["phones", "Smartphones", "PickMeAPhone", "PickAnAndroidForMe"]
    with Pool(4) as p:
        p.map(scrapSub, subs)