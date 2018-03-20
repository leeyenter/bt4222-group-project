

with open("json/reddit-Smartphones.json", "r") as file:
    res = json.load(file)

def parseTime(seconds):
    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(seconds))

#for key, thread in res.items():
#    title = thread['title']
#    text = thread['text']
#    print(title, "#", text)
#    brands, models = getEntities((title + " " + text).lower())
##    print(brands)
##    print(models)
#    #print(getModels(text))
#    for reply in thread['replies']:
#        replyText = reply['text']
    