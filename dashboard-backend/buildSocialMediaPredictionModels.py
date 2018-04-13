import pickle, os, csv
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import make_union
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import make_pipeline

#with open('sm-prediction/facebook_model.pkl', 'rb') as file:
#    fbModel = pickle.load(file)


# For instagram

#import glob
#df = pd.DataFrame()
#for file in glob.glob("../instagram-data/*ig.csv"):
#    brand = file.split("_ig.csv")[0].replace('../instagram-data\\', '')
#    temp_df = pd.read_csv(file)
#    temp_df["brand"] = brand
#    df = pd.concat([df,temp_df], axis=0)
#
#def handle_numbers(string):
#    string = str(string).replace(",","")
#    if string.lower() == 'nan' or string == '-':
#        return None
#    if "k" in string:
#        if "." in string:
#            return int(string.replace("k","00").replace(".",""))
#        else:
#            return int(string.replace("k","00"))
#    if "m" in string:
#        if "." in string:
#            return int(string.replace("m","00000").replace(".",""))
#        else:
#            return int(string.replace("m","000000"))
#    return int(float(string))
#df = df[df.media=="image"]
#df.likes = df.likes.apply(handle_numbers)
#df = df[df.caption.notnull()]
#
#instaMetaDf = pd.read_csv("../instagram-data/brand_ig_data.csv").drop(['n_following', 'description', 'done'], axis=1)
#instaMetaDf = instaMetaDf[instaMetaDf.n_posts > 0].set_index('brand')
#instaMetaDf['n_followers'] = instaMetaDf.n_followers.apply(handle_numbers)
#instaMetaDf.to_pickle('sm-prediction/instaMetaDf.pkl')
#meta_df = meta_df.loc[:, ["brand_ig","n_posts", "n_followers","n_following"]]
#df.rename(index=str, columns={"brand": "brand_ig"}, inplace=True)
#final_df = pd.merge(df,meta_df,how="left",on="brand_ig")
#final_df["n_posts"] = final_df.n_posts.apply(handle_numbers)
#final_df["n_followers"] = final_df.n_followers.apply(handle_numbers)
#final_df = final_df[final_df.likes != 0]
#
#def get_brand_meta(df):
#    return df.loc[:,["n_posts", "n_followers"]]
#get_brand_meta_ft = FunctionTransformer(get_brand_meta, validate=False)
#
#final_df.to_pickle('sm-prediction/instaDf.pkl')
print('Build Instagram model')
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
#with open('sm-prediction/instaUnion.pkl', 'rb') as file:
#    iUnion = pickle.load(file)

from sklearn.ensemble import GradientBoostingRegressor
gbr = GradientBoostingRegressor(loss="ls", learning_rate=0.1, n_estimators=100, subsample=1.0, criterion="friedman_mse", min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_depth=3, min_impurity_decrease=0.0, min_impurity_split=None, init=None, random_state=1, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False, presort="auto")
gbr.fit(iDtm, np.log(instaDf.likes))
with open('sm-prediction/instaGbr.pkl', 'wb') as file:
    pickle.dump(gbr, file)
    
print('Build Facebook model')
#with open('sm-prediction/instaUnion.pkl', 'wb') as file:
#    pickle.dump(iUnion, file)

#with open('sm-prediction/instaGbr.pkl', 'rb') as file:
#    iGbr = pickle.load(file)
#with open('sm-prediction/instaUnion.pkl', 'rb') as file:
#    iUnion = pickle.load(file)

#def predInsta(caption, brand):
#    fbPred = pd.DataFrame({'caption': [caption], 
#                           'n_posts': [instaMetaDf.loc[brand].n_posts], 
#                           'n_followers': [instaMetaDf.loc[brand].n_followers]})
#    predDtm = iUnion.transform(fbPred)
#    return round(np.exp(iGbr.predict(predDtm))[0], 2)

#pd.concat([meta_importance_df_fb,importance_df_fb],axis = 0).reset_index(drop=True).head(20)

#fb_df = pd.read_csv('sm-prediction/fbDf.csv')
#fb_df.page_followers = fb_df.page_followers.apply(lambda x: int(x.replace(",","")))
#fb_df.page_likes = fb_df.page_likes.apply(lambda x: int(x.replace(",","")))
#fb_df = fb_df[fb_df.post_likes != 0]
#fb_df.to_pickle('sm-prediction/fbDf.pkl')
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

#with open('sm-prediction/fbUnion.pkl', 'rb') as file:
#    union_fb = pickle.load(file)

union_fb = make_union(make_pipeline(get_text_fb_ft, vect_fb), get_brand_meta_fb_ft)
dtm = union_fb.fit_transform(fb_df)
#with open('sm-prediction/fbUnion.pkl', 'wb') as file:
#    pickle.dump(union_fb, file)

gbr_fb = GradientBoostingRegressor(loss="ls", learning_rate=0.1, n_estimators=100, subsample=1.0, criterion="friedman_mse", min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_depth=3, min_impurity_decrease=0.0, min_impurity_split=None, init=None, random_state=1, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False, presort="auto")
gbr_fb.fit(dtm, np.log(fb_df.post_likes))
with open('sm-prediction/fbGbr.pkl', 'wb') as file:
    pickle.dump(gbr_fb, file)
#with open('sm-prediction/fbGbr.pkl', 'rb') as file:
#    gbr_fb = pickle.load(file)

def predFacebook(caption, brand):
    fbPred = pd.DataFrame({'post_message': [caption], 
                           'page_likes': [fbMeta.loc[brand].page_likes], 
                           'page_followers': [fbMeta.loc[brand].page_followers]})
    predDtm = union_fb.transform(fbPred)
    return round(np.exp(gbr_fb.predict(predDtm))[0], 2)


# Twitter
    
print('Build Twitter model')

twitterDf = pd.read_pickle('sm-prediction/twitter-df.pkl')
twitterMeta = pd.read_csv('twitter-brand-lookup.csv').groupby('brand').sum()

def get_text(df):
    return df.text
def get_nmedia(df):
    return df.loc[:,["n_followers"]]
#    return np.expand_dims(df.n_media, axis=1)

get_text_ft = FunctionTransformer(get_text, validate=False)
get_nmedia_ft = FunctionTransformer(get_nmedia, validate=False)

vect = CountVectorizer(stop_words="english",ngram_range=(1,2),min_df=4)
twitterUnion = make_union(make_pipeline(get_text_ft, vect), get_nmedia_ft)
twitterUnion.fit(twitterDf)
#with open('sm-prediction/twitter-FeatureUnion2.pkl', 'wb') as file:
#    pickle.dump(union, file)

#with open('sm-prediction/twitter-FeatureUnion2.pkl', 'rb') as file:
#    twitterUnion = pickle.load(file)

gbr = GradientBoostingRegressor()
dtm = twitterUnion.transform(twitterDf)
gbr.fit(dtm, twitterDf.retweet_count)

#retweet_count

#from sklearn.metrics import r2_score, mean_squared_error
#y = gbr.predict(dtm)
#mean_squared_error(y, twitterDf.retweet_count)

with open('sm-prediction/twitter-model2.pkl', 'wb') as file:
    pickle.dump(gbr, file)

#with open('sm-prediction/twitter-model2.pkl', 'rb') as file:
#    twitterModel = pickle.load(file)
    
#def predTwitter(caption, brand):
#    pred = pd.DataFrame({'text': [caption], 'n_followers': [twitterMeta.loc[brand]['num_followers']]})
##    pred = pd.DataFrame({'text': [caption], 'n_media': [0]})
#    predDtm = twitterUnion.transform(pred)
#    return round(twitterModel.predict(predDtm)[0], 2)
#
#def predictImpact(caption, brand):
#    instaLikes = predInsta(caption, brand)
#    fbLikes = predFacebook(caption, brand)
#    twitterRetweets = predTwitter(caption, brand)
#    return [{'platform': 'Facebook', 'count': fbLikes}, 
#            {'platform': 'Instagram', 'count': instaLikes}, 
#            {'platform': 'Twitter', 'count': twitterRetweets}]