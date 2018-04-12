import json, progressbar
import pandas as pd
from datetime import datetime, timedelta

with open('social-media-files/facebook.json', 'r') as file:
    fb = json.load(file)

with open('social-media-files/instagram.json', 'r') as file:
    insta = json.load(file)

with open('social-media-files/tweets.json', 'r') as file:
    twitter = json.load(file)

#instaBrands = pd.read_csv('../instagram-data/brand_ig_data.csv').drop(['description', 'done'], axis=1)
#instaByBrand = {}
#
#for i in range(instaBrands.shape[0]):
#    brand = instaBrands.loc[i,'brand']
#    handle = instaBrands.loc[i,'brand_ig']
#    num_followers = instaBrands.loc[i,'n_followers']
#    if brand not in instaByBrand:
#        instaByBrand[brand] = {}
#    brandPosts = instaByBrand[brand]
#    startDate = None
#    endDate = None
#    if num_followers == '-':
#        continue
#    if type(num_followers) is not float:
#        if 'm' in num_followers:
#            num_followers = float(num_followers.replace('m', '')) * 1000000
#        elif 'k' in num_followers:
#            num_followers = float(num_followers.replace('k', '')) * 1000
#        else:
#            num_followers = float(num_followers)
#    if num_followers > 0:
#        pass
#    else:
#        continue
#    if handle not in insta:
#        continue
#    for date, posts in insta[handle].items():
#        dateObj = datetime.strptime(date, '%Y-%m-%d')
#        if date not in brandPosts:
#            brandPosts[date] = {'comments': 0, 'num_posts': 0, 'likes': 0}
#            if startDate is None or dateObj < startDate:
#                startDate = dateObj
#            if endDate is None or dateObj > endDate:
#                endDate = dateObj
#        for post in posts:
#            try:
#                brandPosts[date]['comments'] += post['comments']
#            except:
#                pass
#            try:
#                brandPosts[date]['likes'] += post['likes']
#            except:
#                pass
#            brandPosts[date]['num_posts'] += 1
#    if len(brandPosts) == 0:
#        instaByBrand.pop(brand)
#        continue
#    if startDate is None:
#        continue
#    i = startDate
#    while i <= endDate:
#        dateStr = i.strftime('%Y-%m-%d')
#        if dateStr not in brandPosts:
#            brandPosts[dateStr] = {'comments': 0, 'num_posts': 0, 'likes': 0}
#        i += timedelta(1)
#    
#    instaByBrand[brand] = brandPosts
#
#oldDict = instaByBrand.copy()
#for key, value in oldDict.items():
#    if len(value) == 0:
#        instaByBrand.pop(key)
#
#with open('insta-by-brand.json', 'w') as file:
#    json.dump(instaByBrand, file)

#twitterBrands = pd.read_csv('twitter-brand-lookup.csv')
#twitterByBrand = {}
#for i in range(twitterBrands.shape[0]):
#    brand = twitterBrands.loc[i,'brand']
#    handle = twitterBrands.loc[i, 'handle']
#    if brand not in twitterByBrand:
#        twitterByBrand[brand] = {}
#    brandPosts = twitterByBrand[brand]
#    
#    startDate = None
#    endDate = None
#    
#    maxVal = 0
#    for date, tweets in twitter[handle].items():
#        maxVal += len(tweets)
#    counter = 0
#    
#    bar = progressbar.ProgressBar(max_value = maxVal)
#    
#    for date, tweets in twitter[handle].items():
#        dateObj = datetime.strptime(date, '%Y-%m-%d')
#        if startDate is None or dateObj < startDate:
#            startDate = dateObj
#        if endDate is None or dateObj > endDate:
#            endDate = dateObj
#        if date not in brandPosts:
#            brandPosts[date] = {'num_posts': 0, 'favourite_count': 0, 'retweet_count': 0}
#        for tweet in tweets:
#            brandPosts[date]['num_posts'] += 1
#            if tweet['favourite_count'] is not None:
#                brandPosts[date]['favourite_count'] += tweet['favourite_count']
#            if tweet['retweet_count'] is not None:
#                brandPosts[date]['retweet_count'] += tweet['retweet_count']
#            counter += 1
#            bar.update(counter)
#    
#    if startDate is not None:
#        i = startDate
#        while i < endDate:
#            dateStr = i.strftime('%Y-%m-%d')
#            if dateStr not in brandPosts:
#                brandPosts[dateStr] = {'num_posts': 0, 'favourite_count': 0, 'retweet_count': 0}
#            i += timedelta(1)
#    
#        twitterByBrand[brand] = brandPosts
#
#with open('twitter-by-brand.json', 'w') as file:
#    json.dump(twitterByBrand, file)
    
facebookBrands = pd.read_csv('facebook-brand-lookup.csv')
facebookByBrand = {}
for i in range(facebookBrands.shape[0]):
    brand = facebookBrands.loc[i,'brand']
    handle = facebookBrands.loc[i, 'handle']
    if brand not in facebookByBrand:
        facebookByBrand[brand] = {}
    brandPosts = facebookByBrand[brand]
    
    startDate = None
    endDate = None
    
    maxVal = 0
    for date, posts in fb[handle].items():
        maxVal += len(fb)
    counter = 0
    
    bar = progressbar.ProgressBar(max_value = maxVal)
    
    for date, posts in fb[handle].items():
        dateObj = datetime.strptime(date, '%Y-%m-%d')
        if startDate is None or dateObj < startDate:
            startDate = dateObj
        if endDate is None or dateObj > endDate:
            endDate = dateObj
        if date not in brandPosts:
            brandPosts[date] = {'num_posts': 0, 'comments': 0, 'likes': 0, 'shares': 0}
        for post in posts:
            brandPosts[date]['num_posts'] += 1
            if post['comments'] is not None:
                brandPosts[date]['comments'] += post['comments']
            if post['likes'] is not None:
                brandPosts[date]['likes'] += post['likes']
            if post['shares'] is not None:
                brandPosts[date]['shares'] += post['shares']
            counter += 1
            bar.update(counter)
    
    if startDate is not None:
        i = startDate
        while i < endDate:
            dateStr = i.strftime('%Y-%m-%d')
            if dateStr not in brandPosts:
                brandPosts[dateStr] = {'num_posts': 0, 'comments': 0, 'likes': 0, 'shares': 0}
            i += timedelta(1)
    
        facebookByBrand[brand] = brandPosts

with open('facebook-by-brand.json', 'w') as file:
    json.dump(facebookByBrand, file)