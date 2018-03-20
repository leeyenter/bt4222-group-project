import requests, re, json, os
from bs4 import BeautifulSoup
from threadManipulator import appendReply, formThreads, printThread

domain = "https://forum.xda-developers.com"

def pullCategories(phone):
    r = requests.get("https://forum.xda-developers.com/"+phone+"/review", timeout = 10)
    soup = BeautifulSoup(r.text, "lxml")
    threads = soup.select(".thread-row")
    results = []
    
    for thread in threads:
        ratings = thread.select_one(".threadrating")
        if ratings is not None:
            rating = len(ratings.select(".fa-star"))+0.5*len(ratings.select(".fa-star-half-o"))
        else:
            rating = 0
        threadTitle = thread.select_one(".threadTitle")
        links = [domain+threadTitle["href"]]
        navs = thread.select(".thread-pagenav")
        for nav in navs:
            if domain+nav["href"] not in links:
                links.append(domain+nav["href"])
        results.append({
                "title": threadTitle.text, 
                "rating": rating, 
                "links": links})
    return results

def pullReviews(phone):
    categories = pullCategories(phone)
    counter = 0
    for category in categories:
        category["threads"] = []
        pastPosts = []
        # text and link in category
        for link in category["links"]:
            postIDs = {}
            r = requests.get(link)
            soup = BeautifulSoup(r.text, "lxml")
            
            for post in soup.select(".postbit-wrapper"):
                time = post.select_one(".time")
                if time is not None:
                    time = time.text.strip()
                    postID = post.select_one(".postbit-anchor")["id"]
                    quotes = []
                    text = post.select_one(".post-text")
                    for quote in text.select(".bbcode-quote"):
                        quoteLink = quote.select_one("a")
                        if quoteLink is not None:
                            quotes.append(quoteLink["href"][quoteLink["href"].rfind("/")+1:])
                        quote.decompose()
                    for s in text.select("script"):
                        s.decompose()
                    text = re.sub("Sent from .+", "", text.text).strip()
                    post = {'text': text, 
                            'time': time, 
                            'postID': postID, 
                            'replies': []}
                    if post in pastPosts:
                        continue
                    else:
                        pastPosts.append(post)
                    if len(quotes) > 0:
                        for quote in quotes:
                            appendReply(post, category["threads"], quote, postIDs)
                            break # problematic when replying to multiple messages
                    else:
                        postIDs[postID] = [len(category['threads'])]
                        category["threads"].append(post)
        
        counter += 1
        print(str(round(counter * 100 / len(categories), 2)) + "% done")
    return categories

def fetchPhone(phone):
    results = pullReviews(phone)
    with open('json/xda-'+phone+'.json', 'w') as file:
        json.dump(results, file)
        
def fetchPhoneList():
    try:
        with open("json/xda-all-phones.json", "r") as file:
            phones = json.load(file)
    except:
        phones = []
    
    r = requests.get("https://forum.xda-developers.com/top")
    soup = BeautifulSoup(r.text, "lxml")
    
    for header in soup.select(".forum-head"):
        heading = header.select_one("h2").select_one("a")
        if heading is not None:
            phoneDict = {'name': heading.text.strip(), 
                         'link': heading['href'][1:]}
            if phoneDict not in phones:
                phones.append(phoneDict)
                
                
    r = requests.get("https://forum.xda-developers.com/new")
    soup = BeautifulSoup(r.text, "lxml")
    
    for header in soup.select(".forum-head"):
        heading = header.select_one("h2").select_one("a")
        if heading is not None:
            phoneDict = {'name': heading.text.strip(), 
                         'link': heading['href'][1:]}
            if phoneDict not in phones:
                phones.append(phoneDict)
    
    with open("json/xda-all-phones.json", "w") as file:
        json.dump(phones, file)
                
    for phoneDict in phones:
        if not os.path.isfile("json/xda-"+phoneDict["link"]+".json"):
            # search the phone
            print("Fetching", phoneDict["name"])
            fetchPhone(phoneDict['link'])

fetchPhoneList()