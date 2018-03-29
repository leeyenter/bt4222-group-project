from textblob import TextBlob
import spacy, re
print("Loading model")
nlp = spacy.load('en')

from nltk.corpus import stopwords
stops = set(stopwords.words("english"))

skip = {"–", "after", "for"}
startTerms = {"NN", "NNS", "VBD", "CD", "VBG", "JJ"} # "NNP", "NNPS", 
containTerms = startTerms.copy()
containTerms.update({"HYPH", '``', "NNP"})
endTerms = {"NN", "NNS", "VBG", "CD"}

def pullPhrases(para, productTokens):
    blob = TextBlob(para)
    sentiment = blob.sentiment
    
    # Start processing
    newPara = re.sub("r\(.+\)", "", para).replace("  ", " ").strip()
    
    pos = nlp(newPara)
    
    # Let's break the sentence down 
    startIndex = 0
    endIndex = 1
    
    paraPhrases = []
    
    while startIndex < len(pos):
        if pos[startIndex].tag_ in startTerms and pos[startIndex].text.lower() not in productTokens:
            # Build the rest of the phrase
            endIndex = startIndex
            while endIndex < (len(pos)-1) and (pos[endIndex].tag_ in containTerms) and pos[endIndex].text.lower() not in productTokens:
                # Expand the search
                endIndex += 1
            while endIndex > startIndex and ((pos[endIndex].tag_ not in endTerms) or pos[endIndex].text.lower() in productTokens):
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
            
            # we may also want to check tfidf, to rmeove useless phrases
            
            paraPhrases.append({"phrase": phrase, "sentiment": sentiment.polarity})
                
            startIndex = endIndex+1
        else:
            # Move on
            startIndex+=1
    return paraPhrases

def extract(text, productTokens):
    phrases = text.split(",")
    results = []
    for phrase in phrases:
        results += pullPhrases(phrase, productTokens)
    return results
