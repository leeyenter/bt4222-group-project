import requests, json, time, os
from bs4 import BeautifulSoup
from threadManipulator import appendReply
from multiprocessing import Pool

from datetime import date, timedelta
today = date.today().strftime("%m-%d-%Y")
ystd = (date.today() - timedelta(1)).strftime("%m-%d-%Y")

def getNextPageLink(soup):
    prev_next = soup.select_one(".pagination")
    if prev_next is not None:
        for a in prev_next.select("a"):
            if "rel" in a.attrs and a["rel"][0] == "next":
                return a["href"]
    return None

def parsePost(link, posts, postIDs):
    r = None
    while r is None:
        try:
            r = requests.get(link, timeout = 10)
        except:
            time.sleep(5)
    soup = BeautifulSoup(r.text, "lxml")
    
    for post in soup.select(".postbody"):
        quotes = []
        for quote in post.select(".bbcode_container"):
            try:
                link = quote.select_one(".quoted_byline").a["href"]
                postID = link[link.rfind("#")+1:]
                quotes.append(postID)
            except:
                pass
            quote.decompose()
        text = post.select_one(".message").text.strip()
        timestamp = post.select_one(".time").text.strip()
        timestamp = timestamp.replace("Today", today).replace("Yesterday", ystd)
        postID = None
        for a in post.select_one(".desc").select("a"):
            if "name" in a.attrs:
                postID = a["name"]
                break
        post = {"postID": postID, 
                "text": text, 
                "time": timestamp, 
                "replies": []}
        if len(quotes) > 0:
            for quote in quotes:
                appendReply(post, posts, quote, postIDs)
        else:
            postIDs[postID] = [len(posts)]
            posts.append(post)
    
    nextPage = getNextPageLink(soup)
    if nextPage is not None:
        parsePost(nextPage, posts, postIDs)

def parsePage(link, filename, depth):
    results = []
    print("Parsing page", link)
    r = None
    while r is None:
        try:
            r = requests.get(link, timeout=10)
        except:
            time.sleep(5)
    soup = BeautifulSoup(r.text, "lxml")
    
    counter = 0
    for link in soup.select(".i"):
        if link.select_one(".c") is not None and "Sticky:" in link.select_one(".c").text:
            continue
        posts = []
        postIDs = {}
        parsePost(link.a["href"], posts, postIDs)
        if len(posts) == 0:
            continue
        results.append({"title": link.a.text.strip(), 
                        "thread": posts})
        counter += 1
        print(str(round(counter*100/len(soup.select(".i")), 2)) + "% done")
    
    with open(filename, 'a') as file:
        json.dump(results, file)
        file.write("\n")
    
    nextPage = getNextPageLink(soup)
    if nextPage is not None:
        parsePage(nextPage, filename, depth + 1)

def parseForum(link, filename):
    parsePage(link, filename, 1)
#    with open(filename, 'w') as file:
#        json.dump(results, file)

#parseForum("https://forums.androidcentral.com/buyers-guides/", "buyers-guides.json")
#parseForum("https://forums.androidcentral.com/community-reviews/", "json/androidcentral-community-reviews.json")
#parseForum("https://forums.androidcentral.com/samsung-galaxy-s7/", "json/androidcentral-samsung-galaxy-s7.json")
#parseForum("https://forums.androidcentral.com/samsung-galaxy-s9-s9-plus/", "json/androidcentral-samsung-galaxy-s9.json")

def parseForumHelper(phone):
    if os.path.exists('json/androidcentral-'+phone['shortname']+'.json'):
        return
    parseForum(phone['link'], "json/androidcentral-"+phone['shortname']+".json")
    #parseForum("https://forums.androidcentral.com/"+phone, "json/androidcentral-"+phone+".json")

if __name__ == "__main__":
    with open('json/androidcentral-allphones.json', 'r') as file:
        phones = json.load(file)
    
    r = requests.get("https://forums.androidcentral.com/")
    soup = BeautifulSoup(r.text, "lxml")
    forums = soup.select(".forumbit_nopost")
    #phones = []
    for forum in forums:
        title = forum.h2
        if "Android Phones" in title.text or "Google" in title.text:
            subPhones = forum.select(".f2title")
            for phone in subPhones:
                if "More" in phone.text:
                    continue
                newPhone = {
                        "name": phone.text.strip(), 
                        "link": phone["href"], 
                        'shortname': phone["href"].replace("https://forums.androidcentral.com/", "").replace("/", "")}
                if newPhone not in phones:
                    print("New phone:", phone.text)
                    phones.append(newPhone)
    with open('json/androidcentral-allphones.json', 'w') as file:
        json.dump(phones, file)
    #phones = ["moto-x4", "moto-z2-force", "oneplus-5-5t", "lg-g2", "samsung-galaxy-note-5", "samsung-galaxy-note-7", "samsung-galaxy-s6", "samsung-galaxy-s7-edge", "community-reviews", "buyers-guides"]

    with Pool(6) as p:
        p.map(parseForumHelper, phones)

#with open("json/androidcentral-samsung-galaxy-s9-s9-plus.json", "r") as file:
#    results = []
#    for line in file:
#        results += json.loads(line)