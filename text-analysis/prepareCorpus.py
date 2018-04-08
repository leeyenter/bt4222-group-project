import json, re, math


#with open('corpus.json', 'r') as file:
#    texts = json.load(file)
#
#text = ' '.join(texts).lower()
#words = re.findall(r"[\w]+'?-?[\w]+", text)
#counts = {}
#for word in words:
#    if word in counts:
#        counts[word] += 1
#    else:
#        counts[word] = 1
#
#oldCounts = counts.copy()
#for word, count in oldCounts.items():
#    if count < 50:
#        counts.pop(word)
#
#with open('ourWordCounts.json', 'w') as file:
#    json.dump(counts, file)
#    

with open("assets/model-all-tokens.json", 'r') as file:
    modelTokens = set(json.load(file))

with open("ourWordCounts.json", "r") as file:
    ourWordCounts = json.load(file)
#
#with open("wordCounts.json", "r") as file:
#    wordCounts = json.load(file)

with open('googlebooksCounts.json', 'r') as file:
    wordCounts = json.load(file)

    
wordScores = {}

for word, count in ourWordCounts.items():
    if word in wordCounts and word not in modelTokens:
        wordScores[word] = math.log(count) / math.log(wordCounts[word])
#    else:
#        wordScores[word] = math.log(count) / math.log(50)

with open("wordScores.json", "w") as file:
    json.dump(wordScores, file)

