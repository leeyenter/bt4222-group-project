import os, json
import pandas as pd

fb_pages = os.listdir("../facebook-crawling")
posts = {}
for filename in fb_pages:
    if '.csv' not in filename:
        continue
    splitName = filename.replace('.csv', '').split('_', 1)
    pageName = splitName[0]
    if pageName not in posts:
        posts[pageName] = {}
    q = splitName[1]
    df = pd.read_csv('../facebook-crawling/'+filename).drop(['Unnamed: 0'], axis=1)
    if df.shape[0] == 0:
        continue
    df['date'] = df.created_time.apply(lambda x: x.split('T', 1)[0])
    df = df.drop('created_time', axis=1)
    for i in range(df.shape[0]):
        row = df.loc[i]
        obj = {
                'comments': row['comments'].item(), 
                'likes': row['likes'].item(), 
                'link': row['link'], 
                'message': row['message'], 
                'shares': row['shares'].item(), 
                'type': row['type']
        }
        if row['date'] not in posts[pageName]:
            posts[pageName][row['date']] = []
        posts[pageName][row['date']].append(obj)

with open('social-media-files/facebook.json', 'w') as file:
    json.dump(posts, file)