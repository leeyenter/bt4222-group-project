import re, time, json

with open("assets/model-fragments.json", "r") as file:
    fragmentLookup = json.load(file)
with open("assets/model-all-tokens.json", "r") as file:
    allModelTokens = json.load(file)
with open("assets/model-brands.json", "r") as file:
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
    for i in range(0, len(words)-1):
        if words[i] not in allModelTokens:
            continue
        for j in range(i+1, min(i+1+MAX_FRAGMENT_SIZE, len(words))):
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
    brandsFound = getBrands(text)
    modelsFound = getModels(text)
    return (brandsFound, modelsFound)

text = "I've been contemplating getting one of these phones but don't know which one to get. I currently own a Huawei p9 lite and it's not bad at all, however I've owned Google products before and been in love with them. My current dilemma is that I'm leaning towards the pixel which costs £729 for 128gb model where as the mate 10 pro is £529 for 128gb. Although I love the pixel 2 XL it doesn't seem worth an extra £200 for the subtle improvements. I'd love to here other people's opinions and experiences."
print(getEntities(text.lower()))
