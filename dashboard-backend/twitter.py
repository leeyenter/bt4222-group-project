import json, os
import pandas as pd
from datetime import datetime
import progressbar

filenames = os.listdir('../twitter-data')
allTweets = {}
bar = progressbar.ProgressBar(max_value = len(filenames))
counter = 0
for filename in filenames:
    if '.csv' not in filename:
        continue
    df = pd.read_csv('../twitter-data/'+filename)
    df['date'] = df.created_at.apply(lambda x: datetime.strptime(x[4:10] + x[-5:], '%b %d %Y').strftime('%Y-%m-%d'))
    
    tweets = {}
    for i in range(df.shape[0]):
        row = df.loc[i]
        if row['date'] not in tweets:
            tweets[row['date']] = []
        tweets[row['date']].append({
                'favourite_count': row['favorite_count'].item(), 
                'text': row['text'], 
                'retweet_count': row['retweet_count'].item()
                })
    allTweets[filename.replace('.csv', '')] = tweets
    counter += 1
    bar.update(counter)

with open('social-media-files/tweets.json', 'w') as file:
    json.dump(allTweets, file)