import json, os
import pandas as pd

filenames = os.listdir('../instagram-data')
posts = {}
for filename in filenames:
    if 'ig.csv' not in filename:
        continue
    channelName = filename.replace('_ig.csv', '')
    df = pd.read_csv('../instagram-data/'+filename)
    try:
        df2 = pd.read_csv('../instagram-data/'+channelName+'_ig_final.csv')
    except:
        continue
    channelPosts = {}
    for i in range(df.shape[0]):
        row = df.loc[i]
        try:
            likes = int(row['likes'].replace(',',''))
        except:
            likes = None
        try:
            comments = int(row['comments'].replace(',', ''))
        except:
            comments = None
        try:
            date = df2.loc[i]['post_datetime'].split('T', 1)[0]
        except:
            continue
        obj = {
                'likes': likes, 
                'media': row['media'], 
                'comments': comments, 
                'url': row['url'], 
                'caption': row['caption']}
        if date not in channelPosts:
            channelPosts[date] = []
        channelPosts[date].append(obj)
    posts[channelName] = channelPosts
    
with open('social-media-files/instagram.json', 'w') as file:
    json.dump(posts, file)