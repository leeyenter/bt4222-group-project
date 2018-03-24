# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 12:19:54 2018

@author: yenter
"""

from textblob import TextBlob
import re
import pandas as pd
import numpy as np
from statistics import median

from nltk.corpus import stopwords
stops = set(stopwords.words("english"))

from buildCorpus import scrapText

skip = {"–", "after", "for"}
#startTerms = {"NN", "NNS", "NNP", "CD", "JJ", "NNPS"}
#endTerms = startTerms.copy()
#endTerms.update({"POS", "DT", "''", "IN", "POS", "RP"})
startTerms = {"NN", "NNS", "VBD", "CD", "VBG", "JJ"} # "NNP", "NNPS", 
containTerms = startTerms.copy()
containTerms.update({"HYPH", '``', "NNP"})
endTerms = {"NN", "NNS", "VBG", "JJ", "CD"}

starterWords = ["a", "an", "and", "the", "it", "is", "this", "to", "we", "i", "were", "had", "have", "but", "although", "was"]

# product -- collection of searches for a given product
# text -- from an entire website
# para -- paras from a given text

product = "Samsung Galaxy S9"
productTokens = product.lower().split(" ")

texts = scrapText(product, set())

def getMeaningfulParas(text):
    output = []
    for para in text:
        if para.count(" ") < 2 or para.count(" . ")*2/para.count(" ") > 0.3:
            continue
        
        words = re.findall(r'(?u)\b\w\w+\b', para)
        unique = set(words)
        nonStop = [word for word in words if word not in stops]
        
        if len(nonStop)/len(words) > 0.8:
            continue
        
        output.append(para)
    return output


# For the entire product, we want to get an idea of which words are 
# useful in describing the product

productCorpus = []
for page in texts:
    productCorpus.append(". ".join(getMeaningfulParas(page)))

# build a dtm to see the relevance of each word
dtm = vect.transform(productCorpus)
wordsCount = pd.DataFrame(np.sum(dtm, axis=0).tolist()[0], index = vect.get_feature_names(), columns = ['score'])


# For each link, we pull the data

print("Creating phraseTfIdf table")
dfPhrases = []
dfSentiments = []
dfTfIdf = []
phraseNlps = []
phraseGroups = []

paras = []
phrases = []

def pullPhrases(para):
    paras.append(para)
    blob = TextBlob(para)
#    print(blob.sentiment, "-", para)
    sentiment = blob.sentiment
    
    # Start processing
    newPara = ""
    skipping = False
    haveBrackets = "(" in para and ")" in para
    for char in para:
        if char == "(" and haveBrackets: 
            # There is a closing bracket
            skipping = True
        if not skipping:
            newPara += char
        if char == ")" and skipping:
            # Close the bracket
            skipping = False
    
#        for token in product.split(" "):
#            reg = re.compile(re.escape(token), re.IGNORECASE)
#            newPara = reg.sub('', newPara)
    
    newPara = newPara.replace("  ", " ")
    
    pos = nlp(newPara)
    
    # Let's break the sentence down 
    startIndex = 0
    endIndex = 1
    
    paraPhrases = []
    
    while startIndex < (len(pos) - 1):
        if pos[startIndex].tag_ in startTerms and pos[startIndex].text.lower() not in productTokens:
            # Build the rest of the phrase
            endIndex = startIndex+1
            while endIndex < (len(pos)-1) and (pos[endIndex].tag_ in containTerms) and pos[endIndex].text.lower() not in productTokens:
                # Expand the search
                endIndex += 1
            while endIndex > startIndex and ((pos[endIndex].tag_ not in endTerms) or pos[endIndex].text.lower() in productTokens):
                endIndex -= 1
            if startIndex < endIndex:
                phrase = ""
                sumTfIdf = 0
                
                for i in range(startIndex, endIndex + 1):
                    if len(phrase) > 0 and (phrase[-1].isalnum() or phrase[-1:] == '"') and pos[i].text[0].isalnum():
                        # Add spacing
                        phrase += " "
                    phrase += pos[i].text
                    try:
                        sumTfIdf += wordsCount.loc[pos[i].text.lower()]["score"]
                    except:
                        pass
                #sumTfIdf = vect.transform([phrase]).sum()
                if sumTfIdf == 0:
                    startIndex = endIndex+1
                    continue
                
#                    print(phrase, sumTfIdf / (endIndex + 1 - startIndex))
                        
                #phrase = phrase.strip()
#                    words1 = set(phrase.split(" "))
                newPos = nlp(phrase)
                # find a suitable group
                
                group = len(dfPhrases)
#                    for i in range(len(phraseNlps)):
#                        if newPos.text == phraseNlps[i].text:
#                            group = phraseGroups[i]
#                            break
##                        words2 = set(phraseNlps[i].text.split(" "))
##                        wordsInCommon = len(words1 & words2) 
##                        if wordsInCommon >= (len(words1)-1) or wordsInCommon >= (len(words2)-1):
##                            group = phraseGroups[i]
##                            break
#                        if newPos.similarity(phraseNlps[i]) > 0.85:
#                            group = phraseGroups[i]
#                            break
                
                # append for other searches to use
                phraseNlps.append(newPos)
                phraseGroups.append(group)
                
                paraPhrases.append(phrase)
                
                tfidfScore = sumTfIdf / (endIndex + 1 - startIndex)
#                    tfidfScore = sumTfIdf
                
                if group == len(dfPhrases):
                    dfPhrases.append([])
                    dfSentiments.append([])
                    dfTfIdf.append([])
                
                if phrase not in dfPhrases[group]:
                    dfPhrases[group].append(phrase)
                dfSentiments[group].append(sentiment.polarity)
                dfTfIdf[group].append(tfidfScore)
                    
            startIndex = endIndex+1
        else:
            # Move on
            startIndex+=1
    phrases.append(paraPhrases)

for textID in range(len(texts)):
    for para in getMeaningfulParas(texts[textID]):
        pullPhrases(para)
    print(str(round((textID+1) * 100 / len(texts), 2)) + "% done")

df = pd.DataFrame({
        'paras': paras, 
        'phrases': phrases})
df.to_csv("C:/Users/yenter/Desktop/phrases.csv")

phraseDf = pd.DataFrame({
        'phrases': dfPhrases, 
        'sentiments': dfSentiments, 
        'tfidf': dfTfIdf})

phraseDf['sentimentsMedian'] = phraseDf['sentiments'].apply(lambda x: median(x))
phraseDf['tfidfMedian'] = phraseDf['tfidf'].apply(lambda x: median(x))
phraseDf['tfidfSum'] = phraseDf['tfidf'].apply(lambda x: sum(x))

#phraseDf.nlargest(30, 'tfidfMedian')[['phrases', 'tfidfMedian']]
#phraseDf[phraseDf['tfidfMedian'] > 0.5]

phraseDf.nlargest(30, 'tfidfMedian')[['phrases', 'sentimentsMedian']]
phraseDf.nlargest(30, 'tfidfMedian')[['phrases', 'sentiments']]
