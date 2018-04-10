from textblob import TextBlob
import spacy, re, json, statistics, math, progressbar
import pandas as pd
import numpy as np
print("Loading model")
nlp = spacy.load('en_core_web_sm')

#print("Loading stopwords")
from nltk.corpus import stopwords
stops = set(stopwords.words("english"))

skip = {"–", "after", "for", "minutes", "phone", "hours", "seconds", "days", "weeks", "months", "times", "second", "time", "minute", "hour", "week", "month", "years", "year", "days", "day", "yrs", "yr", "things"}

with open('assets/model-all-tokens-small.json', 'r') as file:
    skip.update(json.load(file))

startTerms = {"NN", "NNS", "VBD", "CD", "VBG", "JJ"} # "NNP", "NNPS", 
containTerms = startTerms.copy()
containTerms.update({"HYPH", '``', "NNP"})
endTerms = {"NN", "NNS", "VBG", "CD"}

#print("Loading corpus")

with open('wordScores.json', 'r') as file:
    wordScores = json.load(file)
    
#with open('corpus.json', 'r') as file:
#    texts = json.load(file)
#
#from sklearn.feature_extraction.text import TfidfVectorizer
#vect = TfidfVectorizer(min_df = 0.05, max_df = 0.99)
#vect.fit(texts)
#
#tfidfLookup = pd.DataFrame({"idf": vect.idf_}, index = vect.get_feature_names())

print("Done")

def pullPhrases(para, productTokens):
    blob = TextBlob(para)
    sentiment = blob.sentiment
    
    # Start processing
    newPara = re.sub(r"\(.+\)", "", para).replace("  ", " ").strip()
    
    pos = nlp(newPara)
    
    # Let's break the sentence down 
    startIndex = 0
    endIndex = 1
    
    paraPhrases = []
    
    while startIndex < len(pos):
        if pos[startIndex].tag_ in startTerms and pos[startIndex].text.lower() not in productTokens and pos[startIndex].text.lower() not in skip:
            # Build the rest of the phrase
            endIndex = startIndex
            while endIndex < (len(pos)-1) and (pos[endIndex].tag_ in containTerms) and pos[endIndex].text.lower() not in productTokens:
                # Expand the search
                endIndex += 1
                if pos[endIndex].text.lower() in skip:
                    startIndex = endIndex + 1
                    continue
            while endIndex > startIndex + 1 and ((pos[endIndex].tag_ not in endTerms) or pos[endIndex].text.lower() in productTokens):
                endIndex -= 1
            if not pos[endIndex].tag_ in endTerms or pos[endIndex].text.lower() in productTokens:
                startIndex = endIndex+1
                continue
            phrase = ""
            
            for i in range(startIndex, endIndex + 1):
                if len(phrase) > 0 and (phrase[-1].isalnum() or phrase[-1:] == '"') and pos[i].text[0].isalnum():
                    # Add spacing
                    phrase += " "
                phrase += pos[i].text
            
            if "www" in phrase or "http" in phrase or ".com" in phrase:
                startIndex = endIndex+1
                continue
            
            paraPhrases.append({"phrase": phrase, "sentiment": sentiment.polarity})
                
            startIndex = endIndex+1
        else:
            # Move on
            startIndex+=1
    return paraPhrases

def extract(text, productTokens):
    results = []
    phrases = []
    for sentence in text.split('. '):
        phrases += sentence.split(",")
    
    bar = progressbar.ProgressBar(max_value = len(phrases))
    counter = 0
    for phrase in phrases:
        results += pullPhrases(phrase, productTokens)
        counter += 1
        bar.update(counter)
        
    
    filteredPhrases = {}
    if len(results) == 0:
        # no phrases found
        return None
    for phrase in results:
        scores = 0
        phraseWords = phrase['phrase'].lower().split(' ')
        for word in phraseWords:
            if word in wordScores:
                scores += wordScores[word]
        if phrase['phrase'] not in filteredPhrases:
            filteredPhrases[phrase['phrase']] = {
                    #'wordScore': scores, 
                    'wordScore': scores, # / math.log(len(phraseWords) + 1), 
                    'sentiment': [phrase['sentiment']], 
                    'occurences': 1}
        else:
            filteredPhrases[phrase['phrase']]['sentiment'].append(phrase['sentiment'])
            filteredPhrases[phrase['phrase']]['occurences'] += 1
    
    df = pd.DataFrame.from_dict(filteredPhrases, orient='index')
#    df['sentimentMedian'] = df.sentiment.apply(statistics.median)
    df['sentimentsSummary'] = df.sentiment.apply(lambda x: np.round(np.percentile(x, [25, 50, 75]), 4))
    df['sentimentEdges'] = df.sentiment.apply(lambda x: max((np.percentile(x, [25, 75])), key=abs))
    df['absSentiment'] = abs(df.sentimentEdges)
    df['score'] = df.apply(lambda x: math.log(x['occurences']) * math.log(x['wordScore']+1), axis=1)
    df = df[df.score > 0.6]
    df = df[df.absSentiment > 0]
    df = df.drop(['absSentiment', 'wordScore'], axis=1)
    #df = df.sort_values('absSentiment', ascending = False).drop(['absSentiment', 'wordScore', 'sentiment'], axis=1)
    return df

def getTopPhrases(df):
    # Assumes passed in df from extract function above
    best = df.sort_values('sentimentEdges', ascending = False).drop(['sentimentEdges', 'score'], axis=1).head(10)
    worst = df.sort_values('sentimentEdges', ascending = True).drop(['sentimentEdges', 'score'], axis=1).head(10)
    
    return (best, worst)