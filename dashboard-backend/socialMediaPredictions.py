import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import make_union
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import make_pipeline

print("Loading social media prediction assets")
instaMetaDf = pd.read_pickle('sm-prediction/instaMetaDf.pkl')

def get_text(df):
    return df.caption

get_text_ft = FunctionTransformer(get_text, validate=False)

def get_brand_meta(df):
    return df.loc[:,["n_posts", "n_followers"]]

get_brand_meta_ft = FunctionTransformer(get_brand_meta, validate=False)
    
instaDf = pd.read_pickle('sm-prediction/instaDf.pkl')
iVect = CountVectorizer(stop_words='english', max_df=0.3, min_df=4)
iUnion = make_union(make_pipeline(get_text_ft, iVect), get_brand_meta_ft)
iDtm = iUnion.fit_transform(instaDf)

with open('sm-prediction/instaGbr.pkl', 'rb') as file:
    iGbr = pickle.load(file)
    
def predInsta(caption, brand):
    fbPred = pd.DataFrame({'caption': [caption], 
                           'n_posts': [instaMetaDf.loc[brand].n_posts], 
                           'n_followers': [instaMetaDf.loc[brand].n_followers]})
    predDtm = iUnion.transform(fbPred)
    return round(np.exp(iGbr.predict(predDtm))[0], 2)

fb_df = pd.read_pickle('sm-prediction/fbDf.pkl')

def get_text_fb(df):
    return df.post_message

get_text_fb_ft = FunctionTransformer(get_text_fb, validate=False)
def get_brand_meta_fb(df):
    return df.loc[:,["page_likes", "page_followers"]]

fbMeta = fb_df[['brand', 'page_likes', 'page_followers']].drop_duplicates().set_index('brand')

get_brand_meta_fb_ft = FunctionTransformer(get_brand_meta_fb, validate=False)

from sklearn.feature_extraction.text import CountVectorizer
vect_fb = CountVectorizer(stop_words='english', max_df=0.3, min_df=4)

union_fb = make_union(make_pipeline(get_text_fb_ft, vect_fb), get_brand_meta_fb_ft)
dtm = union_fb.fit_transform(fb_df)

with open('sm-prediction/fbGbr.pkl', 'rb') as file:
    gbr_fb = pickle.load(file)

def predFacebook(caption, brand):
    fbPred = pd.DataFrame({'post_message': [caption], 
                           'page_likes': [fbMeta.loc[brand].page_likes], 
                           'page_followers': [fbMeta.loc[brand].page_followers]})
    predDtm = union_fb.transform(fbPred)
    return round(np.exp(gbr_fb.predict(predDtm))[0], 2)


twitterDf = pd.read_pickle('sm-prediction/twitter-df.pkl')
twitterMeta = pd.read_csv('twitter-brand-lookup.csv').groupby('brand').sum()

def get_text(df):
    return df.text
def get_nmedia(df):
    return df.loc[:,["n_followers"]]

get_text_ft = FunctionTransformer(get_text, validate=False)
get_nmedia_ft = FunctionTransformer(get_nmedia, validate=False)

vect = CountVectorizer(stop_words="english",ngram_range=(1,2),min_df=4)
twitterUnion = make_union(make_pipeline(get_text_ft, vect), get_nmedia_ft)
twitterUnion.fit(twitterDf)

with open('sm-prediction/twitter-model2.pkl', 'rb') as file:
    twitterModel = pickle.load(file)
    
def predTwitter(caption, brand):
    pred = pd.DataFrame({'text': [caption], 'n_followers': [twitterMeta.loc[brand]['num_followers']]})
    predDtm = twitterUnion.transform(pred)
    return round(twitterModel.predict(predDtm)[0], 2)

def predictImpact(caption, brand):
    instaLikes = predInsta(caption, brand)
    fbLikes = predFacebook(caption, brand)
    twitterRetweets = predTwitter(caption, brand)
    return [{'platform': 'Facebook', 'count': fbLikes}, 
            {'platform': 'Instagram', 'count': instaLikes}, 
            {'platform': 'Twitter', 'count': twitterRetweets}]
