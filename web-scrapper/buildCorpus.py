import requests, re, io, csv, ast
import os.path
from multiprocessing import Pool
from urllib import request
from bs4 import BeautifulSoup
# import operator

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Called on each search result, to pull relevant keywords
def getText(link):
    # print(" - ", link)
    try:
        r = requests.get(link, verify = False, timeout = 5)
    except KeyboardInterrupt:
        raise
    except:
        # print("Error")
        return ""
    
    b = BeautifulSoup(r.text, "lxml")
    [b.extract() for b in b(['script', 'link', 'meta', 'style'])]
    text = [b.extract() for b in b(['p', 'div'])]
    output = ""
    for excerpt in text:
        found = excerpt.get_text(separator = " ").strip().replace("\xa0", ". ").replace("\n", ". ").replace("\t", ". ").replace("\r", ". ").strip()
        sentences = found.split(". ")
        for sentence in sentences:
            stripped = sentence.strip()
            if stripped.count(" ") < 5:
                continue
            output += stripped + ". "

    while "  " in output: # Remove double spaces
        output = output.replace("  ", " ")
    while ". . " in output:
        output = output.replace(". . ", ". ")

    return output

def scrapText(product, pastLinks):
    print("Scrapping reviews for " + product)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get("https://duckduckgo.com/html?q=\""+product.replace(" ", "+")+"\"", headers = headers)
    soup = BeautifulSoup(r.text, "lxml")

    links = []
    for linkItem in soup.select(".result__a"):
        if linkItem["href"] not in pastLinks:
            links.append(linkItem["href"])
            pastLinks.add(linkItem["href"])
    
    with Pool(10) as p:
        texts = p.map(getText, links)
    
    return texts

def scrapProduct(product, pastLinks):
    path = "full-reviews/"+re.sub(r'[^a-zA-Z0-9()+]', '_', product)+".txt"
    if not os.path.isfile(path):
        texts = scrapText(product, pastLinks)
        with io.open(path, mode="w", encoding='utf-8') as file:
            for text in texts:
                if text != "":
                    file.write(text+"\n")

def scrapProducts():
    products = []
    pastLinks = set()
    with open("all_brand_models.csv") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 0:
                continue # skip empty rows
            brand = row[0]
            try:
                models = ast.literal_eval(row[1])
            except:
                print(row[0])
                print(row[1])
                break
            for model in models:
                products.append(brand + " " + model)
    
    for product in products:
        scrapProduct(product, pastLinks)

