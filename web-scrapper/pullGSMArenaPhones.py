import requests, json
from bs4 import BeautifulSoup
from multiprocessing import Pool

def searchPage(page):
    phones = []
    r = requests.get('https://www.gsmarena.com/'+page['link'])
    soup = BeautifulSoup(r.text, 'lxml')
    for phone in soup.select_one(".makers").select("a"):
        phoneName = phone.text
        phoneLink = phone['href']
        phones.append({'name': page['brand'] + ' ' + phoneName, 'link': phoneLink})
    return phones

if __name__ == '__main__':
    
    r = requests.get("https://www.gsmarena.com")
    soup = BeautifulSoup(r.text, "lxml")
    counter = 0
    brands = soup.select_one(".brandmenu-v2").select_one("ul").select("a")
    pagesToSearch = []
    
    for brand in brands:
        brandName = brand.text
        brandLink = brand['href']
        r = requests.get('https://www.gsmarena.com/'+brandLink)
        soup = BeautifulSoup(r.text, 'lxml')
        try:
            pages = soup.select_one('.nav-pages').select('a')
            for page in pages:
                pagesToSearch.append({'brand': brandName, 'link': page['href']})
        except:
            pass
        pagesToSearch.append({'brand': brandName, 'link': brandLink})
        
    
    with Pool(16) as p:
        phoneList = p.map(searchPage, pagesToSearch)
    
    phones = []
    for phone in phoneList:
        phones += phone
    
    with open('json/gsmarena-all-phones.json', 'w') as file:
        json.dump(phones, file)