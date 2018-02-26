import requests, re
from urllib import request
from io import BytesIO
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from nltk.corpus import stopwords
stops = set(stopwords.words("english"))
from bs4 import BeautifulSoup
import operator

import spacy
nlp = spacy.load('en_core_web_sm')

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

skip = {"–", "after", "for"}
startTerms = {"NN", "NNS", "NNP", "CD", "JJ", "NNPS"}
endTerms = startTerms.copy()
endTerms.update({"POS", "DT", "''", "-", "IN", "POS", "RP"})

# Called on each search result, to pull relevant keywords
def getText(link, keywords, haveKeyword):
    print("---", link)
    try:
        r = requests.get(link, verify = False, timeout = 5)
    except:
        return []
    b = BeautifulSoup(r.text, "lxml")
    [b.extract() for b in b(['script', 'link', 'meta', 'style'])]
    # assume the text will only be in p and div
    text = [b.extract() for b in b(['p', 'div'])]
    
    for excerpt in text: # iterate through each para/div
        # Change newline tags to sentences
        found = excerpt.get_text(separator = " ").strip().replace("\xa0", ". ").replace("\n", ". ").replace("\t", ". ").replace("\r", ". ").strip()
        while "  " in found: # Remove double spaces
            found = found.replace("  ", " ")
        if found.count("/") > 2: # likely a link
            continue
            
        words = found.split(" ")
        if len(words) > 15:
            # Time to add it in
            # Check if it has the name of the product
            foundCleaned = [word for word in words if word not in stops]
            uniqueWords = set(foundCleaned)
            maxCount = 0
            for word in uniqueWords:
                maxCount = max(maxCount, found.count(word)) # count the number of unique words (excluding stopwords)
            if maxCount/len(foundCleaned) > 0.15:
                # ignored.append(found)
                continue
                #pass
            elif len(foundCleaned) / len(words) > 0.73:
                # Too many unique words
                continue
            else:
                haveKeywords = any(keyword in found.lower() for keyword in keywords)
                sentences = re.split('\. |! |; ', found) #found.split(". ")
                for sentence in sentences:
                    
                    # Remove parentheses
                    while "(" in sentence and ")" in sentence:
                        startBracket = sentence.find("(")
                        endBracket = sentence.find(")")
                        if startBracket > -1 and endBracket > startBracket:
                            sentence = sentence[0:startBracket].strip() + " " + sentence[endBracket+1:].strip()
                        else:
                            break
                        sentence = sentence.strip()

                    # Remove ending punctuation
                    while len(sentence) > 0 and (sentence[len(sentence)-1] == "." or sentence[len(sentence)-1] == ","):
                        sentence = sentence[0:len(sentence)-1]
                        
                    if len(sentence) == 0:
                        continue
                    
                    words = sentence.split(" ")
                    
                    if len(words) > 2:
                        if haveKeywords:
                            if sentence not in haveKeyword:
                                sentenceToAdd = ""
                                for word in words:
                                    if len(word) > 0:
                                        sentenceToAdd += word + " "
                                haveKeyword.append(sentenceToAdd.strip())

def scrapReviews(product):
    haveKeyword = []
    keywords = product.lower().split(" ")

    tokens = set()
    for token in keywords:
        tokens.add(token)

    starterWords = ["a", "an", "and", "the", "it", "is", "this", "to", "we", "i", "were", "had", "have", "but", "although", "was"] + keywords

    print("Scrapping reviews for " + product)

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get("https://duckduckgo.com/html?q=\""+product.replace(" ", "+")+"\"", headers = headers)
    soup = BeautifulSoup(r.text, "lxml")

    for linkItem in soup.select(".result__a"):
        getText(linkItem["href"], keywords, haveKeyword)

    nouns = {}
    wordCount = {}
    nounLemmas = {}
    parseHash = {}

    def parse(item):
        if item not in parseHash:
            parseHash[item] = nlp(item)
        return parseHash[item]

    def addPhrase(item, nlps, output):
        if item == "":
            return
        s = parse(item.lower())
        add = True
        for otherItems in nlps:
            if s.similarity(otherItems) > 0.8 or s.text in otherItems.text or otherItems.text in s.text:
                add = False
                break
        if add:
            output.append(item)
            nlps.append(s)

    for item in haveKeyword:
        words = item.split(" ")
        sentence = words[0]
        
        for item in words[1:]:
            if len(item) == 0: # multiple spaces are interpreted as empty tokens
                continue
            if sentence[len(sentence)-1].isalnum() and item[0].isalnum():
                sentence += " "
            sentence += item
        
        pos = parse(sentence)
        
        startIndex = 0
        endIndex = 1
        while startIndex < (len(pos) - 1):
            if pos[startIndex].tag_ in startTerms and pos[startIndex].text not in skip:
                endIndex = startIndex+1
                while endIndex < len(pos) and (pos[endIndex].text not in skip) and (pos[endIndex].tag_ in endTerms):
                    endIndex += 1
                while endIndex > (startIndex+1) and (pos[endIndex-1].tag_ not in startTerms or not pos[endIndex-1].text.isalnum()):
                    endIndex -= 1
                if endIndex != startIndex+1:
                    tokens = []
                    lemmas = []
                    for i in range(startIndex, endIndex):
                        tokens.append(pos[i].text)
                        if len(pos[i].lemma_) > 3 and pos[i].lemma_ not in starterWords:
                            lemmas.append(pos[i].lemma_)
                    phrase = tokens[0]
                    for token in tokens[1:]:
                        if len(phrase) > 0 and phrase[len(phrase)-1].isalnum() and token[0].isalnum():
                            phrase += " "
                        phrase += token
                    if phrase in nouns:
                        nouns[phrase] += 1
                    else:
                        nouns[phrase] = 1
                    
                    for token in lemmas:
                        if token in wordCount:
                            wordCount[token] += 1
                        else:
                            wordCount[token] = 1
                    nounLemmas[phrase] = lemmas
                startIndex = endIndex
            else:
                startIndex += 1
    scores = {}
    for noun in nounLemmas:
        score = 0
        for token in nounLemmas[noun]:
            score += wordCount[token]
        scores[noun] = score / (len(nounLemmas))

    nouns = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)

    output = []
    nlps = []

    for noun, nounScore in nouns:
        if " and " in noun:
            toAdd = []
            phrase = noun
            while " and " in phrase and (phrase.find(" and ") + 5) < len(phrase):
                phraseScore = 0
                pos = parse(phrase)
                for item in pos:
                    if item.lemma_ in wordCount:
                        phraseScore += wordCount[item.lemma_]
                phraseScore /= len(pos)
                
                p = [phrase[:phrase.find(" and ")], phrase[phrase.find(" and ") + 5:]]
                pScore = [0,0]
                for i in range(0, 2):
                    pos = parse(p[i])
                    score = 0
                    for item in pos:
                        if item.lemma_ in wordCount:
                            score += wordCount[item.lemma_]
                    pScore[i] = score / (len(pos))
                
                if (pScore[0] + pScore[1]) - (phraseScore * 2) > 0:
                    toAdd.append(p[0])
                    if " and " not in p[1]:
                        toAdd.append(p[1])
                else:
                    if " and " not in p[1]:
                        toAdd.append(phrase)
                phrase = p[1]
            for item in toAdd:
                addPhrase(item, nlps, output)
        else:
            addPhrase(noun, nlps, output)
    return (output)
