import csv, spacy, ast, os, progressbar
import numpy as np

print('Loading spacy model')
nlp = spacy.load('en_core_web_lg')
print('Done')

filenames = os.listdir('results/phrases/xda/')
bar = progressbar.ProgressBar(max_value = len(filenames))

counter = 0
for filename in filenames:
    model = filename.replace('.csv', '')

    phrases = []
    phrasePos = {}
    
    with open('results/phrases/xda/' + filename, 'r') as file:
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
        continue
    
    for phrase in phrases:
        phrase['score'] /= len(phrase['phrase'])
        phrase['sentiments'] = np.percentile(phrase['sentiments'], [10, 25, 50, 75, 90])
    
    import pandas as pd
    df = pd.DataFrame(phrases)
    df['sentimentEdges'] = df.sentiments.apply(lambda x: max(x, key=abs))
    best = df.sort_values('sentimentEdges', ascending = False).drop(['sentimentEdges', 'score'], axis=1).head(10)
    worst = df.sort_values('sentimentEdges', ascending = True).drop(['sentimentEdges', 'score'], axis=1).head(10)
    
    best.to_json('results/phrases/xda-json/' + model + '_best.json', orient='records')
    worst.to_json('results/phrases/xda-json/' + model + '_worst.json', orient='records')
    
    counter += 1
    bar.update(counter)