import json, os

texts = []

def parseAndroidCentral(thread):
    global texts
    for post in thread:
        texts.append(post['text'])
        parseAndroidCentral(post['replies'])

def parseReddit(thread):
    global texts
    text = thread['text']
    if "title" in thread:
        text += " " + thread['title']
    texts.append(text)
    for reply in thread['replies']:
        parseReddit(reply)
    
for filename in os.listdir("../web-scrapper/json"):
    if "xda" in filename and "all-phones" not in filename:
        with open("../web-scrapper/json/"+filename, "r") as file:
            res = json.load(file)
        for category in res:
            for post in category['threads']:
                texts.append(post['text'])
    elif "androidcentral" in filename and "allphones" not in filename:
        with open("../web-scrapper/json/"+filename, "r") as file:
            for row in file:
                for thread in json.loads(row):
                    parseAndroidCentral(thread['thread'])
    elif "reddit" in filename:
        with open("../web-scrapper/json/"+filename, "r") as file:
            for key, thread in json.load(file).items():
                parseReddit(thread)

with open("corpus.json", "w") as file:
    json.dump(texts, file)