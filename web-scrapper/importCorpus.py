from os import listdir

def loadCorpus():
    FULL_REVIEWS_PATH = "full-reviews"
    fileNames = listdir(FULL_REVIEWS_PATH)
    textList = []

    counter = 0
    for fileName in fileNames:
        with open(FULL_REVIEWS_PATH+"/"+fileName, encoding="utf-8") as file:
            text = file.read()
            textList.append(text)
            counter += 1
            if counter%40 == 0:
                print( str(round(counter/len(fileNames)*100, 2)) + "% done")
            # texts[fileName] = text
    
    return textList


print("Loading spaCy...")
import spacy
nlp = spacy.load('en_core_web_sm')

FULL_REVIEWS_PATH = "full-reviews"

print("Loading corpus...")
textList = loadCorpus()

print("Fitting vectorizer...")
from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer(min_df = 0.05, max_df = 0.9)
vect.fit(textList)

print("Done")