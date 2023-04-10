import difflib
import re
import bs4
import json
import pandas
import requests
import amazon
import ebay
import functions
from bs4 import BeautifulSoup
from joblib import Parallel, delayed

# TODO Make logic program
amazon_items = amazon.amz_items()

def get_ebay_list(amz):
    _amz_link, amz_title, amz_price, amz_brand, amz_tm, amz_category = amz
    amz_title_e = functions.title_transform(amz_title)
    e = ebay.EbayItemsList()
    ebay_items = e.ebay_items(str(amz_title_e))
    ebay_links = {}

    # Amazon formulas to calculate margin
    #margin = amz_price * 0.85 - ebay_price
    #roi = margin / float(ebay_price) * 100

    for i, value in ebay_items.items():
        sim = functions.similarity(amz_title, i)
        margin = amz_price * 0.85 - float(value[1])
        roi = margin / float(value[1]) * 100
        if sim > 60 and value[2] >= 97 and value[3] >= 500 and margin >= 2 and roi >= 30:
            ebay_links[ebay_items[i][0]] = {"name": i, "similarity": sim, "price": value[1],
                                          "img": 'no', 'link': value[0]}

    if len(ebay_links) == 0:
        amz_title_e = amz_title_e.split('+')
        amz_title_e = '+'.join(amz_title_e[:len(amz_title_e) // 2])
        ebay_items = e.ebay_items(amz_title_e)

        for i, value in ebay_items.items():
            sim = functions.similarity(amz_title, i)
            margin = amz_price * 0.85 - float(value[1])
            roi = margin / float(value[1]) * 100
            if sim > 60 and value[2] >= 97 and value[3] >= 500 and margin >= 2 and roi >= 30:
                ebay_links[ebay_items[i][0]] = {"name": i, "similarity": sim, "price": ebay_items[i][1],
                                                "img": ebay_items[i][2], 'link': ebay_items[i][0]}

    link_list = sorted(ebay_links.items(), key=lambda x: x[1]['similarity'], reverse=True) # sorted items by max value

    # Ebay item block
    result = []
    for link in link_list:
        try:
            page = requests.get(link[0], timeout=100)
        except requests.exceptions.ConnectionError:
            print("Connection refused")
            requests.status_code = "Connection refused"

        soup = BeautifulSoup(page.text, 'html.parser')
        try:
            ebay_available = soup.find('div', {'class': 'd-quantity__availability'}).text
            ebay_available = ' '.join([x for x in ebay_available.split(' ') if x not in ['available', "/", 'sold', "More", 'than']])

            if 'Last One' in ebay_available:
                ebay_available = 1
            else:
                ebay_available = ebay_available.split()
                ebay_available = int(ebay_available[0])
        except:
            ebay_available = 0

        if ebay_available >= 5:
            result.append({"link": ebay_links[link[0]]})

    return {"title": amz_title, "price": amz_price, "link": _amz_link, "category": amz_category, "tm": amz_tm, "ebay": result}

final = Parallel(n_jobs=-1)(delayed(get_ebay_list)(x) for x in amazon_items)

ff = [x for x in final if x['ebay']]

new_f = []

for x in ff:
    max_sim = max([y['link']['similarity'] for y in x['ebay']])
    t = x
    t['max_sim'] = max_sim
    new_f.append(t)

ff = sorted(new_f, key=lambda x: x['max_sim'], reverse=True)
s = json.dumps(ff)
with open('./data/3.json', 'w') as f:
    f.write(s)