import csv, spacy, ast, os, progressbar, sys
import numpy as np

maxInt = sys.maxsize
decrement = True

while decrement:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

print('Loading spacy model')
nlp = spacy.load('en_core_web_lg')
print('Done')

filenames = os.listdir('results/phrases/androidcentral/')
bar = progressbar.ProgressBar(max_value = len(filenames))

counter = 0
for filename in filenames:
    model = filename.replace('.csv', '')
    
    if os.path.exists('results/phrases/androidcentral-json/' + model + '_best.json'):
        counter += 1
        bar.update(counter)
        continue

    phrases = []
    phrasePos = {}
    
    with open('results/phrases/androidcentral/' + filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == '':
                continue
            #phrases.append(row)
            phrase = row[0]
            sentiments = ast.literal_eval(row[1])
            occurrences = int(row[2])
            score = float(row[5])
            #occurences = row[1]
            #sentimentScore = row[2]
            pos = nlp(phrase)
            
            group = None
            for otherPos, position in phrasePos.items():
                if pos.similarity(otherPos) > 0.815:
                    # Same group
                    group = position
                    break
                
            if group is None:
                # Create new group
                group = len(phrases)
                phrases.append({
                        'phrase': [phrase], 
                        'sentiments': sentiments, 
                        'occurrences': occurrences, 
                        'score': score})
            else:
                phrases[group]['phrase'].append(phrase)
                phrases[group]['sentiments'] += sentiments
                phrases[group]['occurrences'] += occurrences
                phrases[group]['score'] += score
            phrasePos[pos] = group
    
    if len(phrases) == 0:
        counter += 1
        bar.update(counter)
        continue
    
    for phrase in phrases:
        phrase['score'] /= len(phrase['phrase'])
        phrase['sentiments'] = np.percentile(phrase['sentiments'], [10, 25, 50, 75, 90])
    
    import pandas as pd
    df = pd.DataFrame(phrases)
    df['sentimentEdges'] = df.sentiments.apply(lambda x: max(x, key=abs))
    best = df.sort_values('sentimentEdges', ascending = False).drop(['sentimentEdges', 'score'], axis=1).head(10)
    worst = df.sort_values('sentimentEdges', ascending = True).drop(['sentimentEdges', 'score'], axis=1).head(10)
    
    best.to_json('results/phrases/androidcentral-json/' + model + '_best.json', orient='records')
    worst.to_json('results/phrases/androidcentral-json/' + model + '_worst.json', orient='records')
    
    counter += 1
    bar.update(counter)