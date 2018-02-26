from os import listdir
import re
FULL_REVIEWS_PATH = "full-reviews"
fileNames = listdir(FULL_REVIEWS_PATH)
textList = []
texts = {}

for fileName in fileNames:
    with open(FULL_REVIEWS_PATH+"/"+fileName, encoding="utf-8") as file:
        text = file.read()
        textList.append(text)
        texts[fileName] = text

from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer()
vect.fit(textList)

import numpy as np
import pandas as pd
import math

def pullTopBlurbs(product):
    sentences = list(filter(lambda x: x.count(" ") > 4, map(lambda x: x.strip(), re.split('[!?.\n]', texts[product]))))
    # Maybe do more processing for each sentence here
    dtm = vect.transform(sentences)
    df = pd.DataFrame({'sentences': sentences, 'sumTFIDF': pd.DataFrame(np.sum(dtm, axis=1))[0]})
    df["wordCount"] = df["sentences"].apply(lambda x: x.count(" ")+1)
    df["score"] = df["sumTFIDF"] / df["wordCount"]
    df["scoreLog"] = df["sumTFIDF"] / df["wordCount"].map(lambda x: math.log(x))
    pd.set_option('display.max_colwidth', 200)
    df.nlargest(10, 'score')['sentences']

#pullTopBlurbs("lg_g5.txt")