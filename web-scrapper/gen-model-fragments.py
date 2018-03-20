import json, re, csv, ast

#with open("json/androidcentral-allphones.json", "r") as file:
#    androidCentralPhones = json.load(file)

#with open("json/xda-all-phones.json", "r") as file:
#    phones = json.load(file)

brands = set()

phones = []
with open("all_brand_models.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 0:
            continue
        brand = row[0]
        brands.add(brand)
        models = set()
        modelsFound = ast.literal_eval(row[1])
        for model in modelsFound:
            name = re.sub(r"\([a-zA-Z0-9 ]+\)", "", model).replace("Verizon", "").replace("AT&T", "").strip()
            models.add(name)
        for model in models:
            phones.append(brand+" "+model)

allModels = []

skipWords = {"galaxy", "note", "one", "eyes", "lite", "view", "phone", 
             "life", "active", "motion", "alpha", "plus", "performance", 
             "desire", "cam", "screen", "mate", "xperia", 'style', 'ai', 
             'steel', 'icon', 'premium', 'data', 'messenger', 'express', 
             'zoom', 'fusion', 'lifestyle', 'surface', 'zero', 'tribute', 
             'skin', 'amaze', 'non', 'magic', 'led', 'emerge', 'boot', 
             'lemon', 'iris', 'wave', 'live', 'pioneer', 'youth', 'star',
             'speed', 'metal', 'chat', 'duo', 'two', 'mark', 'check', 
             'compass', 'giant', 'virtue', 'cdma', 'cube'}

for phone in phones:
    name = phone#['name']
    name = re.sub(r"\([a-zA-Z0-9]+\)", "", name).replace("Verizon", "").replace("AT&T", "").strip()
    allModels.append(name)

uniqueKeys = set()
modelExcludeWords = {}

fragments = set()
allModelTokens = set()

for name in allModels:
    brand, model = name.split(" ", 1)
    brands.add(brand)
    modelTokens = name.lower().split(" ")
    allModelTokens.update(modelTokens)
    for i in range(len(modelTokens)):
        for j in range(max(i+1, 2), len(modelTokens)+1):
            fragment = ' '.join(modelTokens[i:j])
            if len(fragment) == 1:
                continue
            if fragment.isdigit():
                continue
            if fragment in skipWords:
                continue
            fragments.add(fragment)
            
fragmentLookup = {}

for fragment in fragments:
    foundInLast = False
    count = 0
    models = []
    for name in allModels:
        if fragment in name.lower():
            models.append(name)
            count += 1
            if len(name) - len(fragment) == name.lower().find(fragment):
                foundInLast = True
    if not foundInLast and count > 1:
        # Meaningless 
        continue
    model = models[0]
    if len(models) > 1:
        fragmentBrands = set()
        for modelName in models:
            fragmentBrands.add(modelName[:modelName.find(" ")])
        if len(fragmentBrands) == 1:
            # subset
            # find the shortest model perhaps?
            for other in models[1:]:
                
                if len(other) < len(model):
                    model = other
        else:
            # different brands
            # ignore
            continue
    fragmentLookup[fragment] = model

with open("assets/model-fragments.json", "w") as file:
    json.dump(fragmentLookup, file)

with open("assets/model-brands.json", "w") as file:
    json.dump(list(brands), file)
    
with open("assets/model-all-tokens.json", "w") as file:
    json.dump(list(allModelTokens), file)