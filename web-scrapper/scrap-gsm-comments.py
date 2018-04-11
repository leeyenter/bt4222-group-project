import json, requests, progressbar, os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from textblob import TextBlob
import numpy as np
from multiprocessing import Pool

todayStr = datetime.strftime(datetime.now(), '%d %b %Y')

def pullComments(gsmLink):
    if os.path.exists('json/gsm-'+gsmLink.replace('.php', '.json')):
        return
    
    splitLink = gsmLink.split('-', 1)
    reviewsLink = splitLink[0] + '-reviews-' + splitLink[1]
    
    r = requests.get('https://www.gsmarena.com/'+reviewsLink)
    soup = BeautifulSoup(r.text, 'lxml')
    commentPages = [reviewsLink]
    reviewPageStem = reviewsLink.replace('.php', '') + 'p'
    
    try:
        lastPage = soup.select_one('.nav-pages').select('a')[-2].text
        for i in range(2, int(lastPage)+1):
            commentPages.append(reviewPageStem+str(i)+'.php')
    except:
        pass
    
    posts = []
    startDate = None
    endDate = None
    dateCounts = {}
    dateSentiments = {}
    
    count = 0
    bar = progressbar.ProgressBar(max_value = len(commentPages))
    
    for link in commentPages:
        r = requests.get('https://www.gsmarena.com/'+link)
        soup = BeautifulSoup(r.text, 'lxml')
        for post in soup.select('.user-thread'):
            postText = post.select_one('.uopin')
            for x in postText.select('a'):
                x.decompose()
            for x in postText.select('span'):
                x.decompose()
            postText = postText.text
            blob = TextBlob(postText)
            time = post.select_one('time').text
            if 'ago' in time:
                time = todayStr
            posts.append({'text': postText, 'date': time})
            
            timeObj = datetime.strptime(time, '%d %b %Y')
            date = timeObj.strftime("%Y-%m-%d")
            
            if date in dateCounts:
                dateCounts[date] += 1
                dateSentiments[date].append(blob.sentiment.polarity)
            else:
                dateCounts[date] = 1
                dateSentiments[date] = [blob.sentiment.polarity]
                
                if startDate is None or timeObj < startDate:
                    startDate = timeObj
                if endDate is None or timeObj > endDate:
                    endDate = timeObj
        count += 1
        bar.update(count)
    
    if startDate is None:
        # no posts
        return
    dateSentimentsSummary = {}
    i = startDate
    while i <= endDate:
        dateStr = i.strftime('%Y-%m-%d')
        if dateStr not in dateCounts:
            dateCounts[dateStr] = 0
            dateSentimentsSummary[dateStr] = None
        else:
            dateSentimentsSummary[dateStr] = list(np.percentile(dateSentiments[dateStr], [25, 50, 75]))
        i += timedelta(1)
    
    with open('json/gsm-'+gsmLink.replace('.php', '.json'), 'w') as file:
        json.dump(posts, file)
    
    obj = {'num_posts': dateCounts, 'sentiments': dateSentimentsSummary}
    with open('../text-analysis/results/gsmarena/'+gsmLink.replace('.php', '_interest.json'), 'w') as file:
        json.dump(obj, file)

if __name__ == '__main__':
    # Read in the phone models
    phones = []
    with open('all-phones.json', 'r') as file:
        for phone, value in json.load(file).items():
            phones.append(value['gsm'])
    with Pool(16) as p:
        p.map(pullComments, phones)

