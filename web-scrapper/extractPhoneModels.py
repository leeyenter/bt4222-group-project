import re, time, json

with open("assets/model-fragments-small.json", "r") as file:
    fragmentLookup = json.load(file)
with open("assets/model-all-tokens-small.json", "r") as file:
    allModelTokens = json.load(file)
with open("assets/model-brands-small.json", "r") as file:
    brands = json.load(file)

MAX_FRAGMENT_SIZE=0 # so that we don't have to search till the end of the string
for frag, index in fragmentLookup.items():
    if frag.count(" ") + 1 > MAX_FRAGMENT_SIZE:
        MAX_FRAGMENT_SIZE = frag.count(" ") + 1

rgx = re.compile("[\w+]+") # include + also

def getBrands(text):
    brandsFound = set()
    words = set(rgx.findall(text))
    for brand in brands:
        if brand.lower() in words:
            brandsFound.add(brand)
    return brandsFound

def getModels(text):
    modelsFound = set()
    fragmentsFound = set()
    fragmentsAccepted = {}
    
    words = rgx.findall(text)
    for i in range(0, len(words)):
        if words[i] not in allModelTokens:
            continue
        for j in range(i+1, min(i+1+MAX_FRAGMENT_SIZE, len(words)+1)):
            fragment = " ".join(words[i:j])
            if fragment in fragmentLookup:
                fragmentsFound.add(fragment)
    for fragment in sorted(fragmentsFound, key=len, reverse=True):
        # we iterate through the fragments we've found, to ensure that 'smaller' 
        # model names are not accidentally extracted (e.g. Pixel vs Pixel 2)
        found = False
        for frag, index in fragmentsAccepted.items():
            if fragment in frag and text.find(frag) + frag.find(fragment) == text.find(fragment):
                found = True
                break
        if not found:
            fragmentsAccepted[fragment] = text.find(fragment)
    for frag, index in fragmentsAccepted.items():
        modelsFound.add(fragmentLookup[frag])
    return modelsFound

def getEntities(text):
    lowered = text.lower()
    brandsFound = getBrands(lowered)
    modelsFound = getModels(lowered)
    for model in modelsFound:
        brandsFound.add(model.split(" ", 1)[0])
    return (brandsFound, modelsFound)