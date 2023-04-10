import json, requests
from fuzzywuzzy import fuzz
from sortedcollections import OrderedSet

def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    return fuzz.token_sort_ratio(normalized1, normalized2)

def tm_checker(amz_brand):
    with open('black_tm.txt', 'r+') as b_tm:
        black_brand = b_tm.read()
    black_brand = black_brand.split("\n")

    if amz_brand in black_brand:
        return 'TM'
    else:
        page_tm = requests.get(
            'https://search-api.trademarkia.com/api/basic/us?input_query=%s&filing_date=-1406419200,1674476552&page=1&sort_by=status_date&sort_asc=false&status=all&exact_match=false&date_query=false' % amz_brand)
        try:
            data = json.loads(page_tm.text)
        except json.decoder.JSONDecodeError:
            return 'NO TM'

        try:
            ls = [x for x in data['body']['data'] if x['status_code'] >= 700]
        except:
            return 'NO TM'
        if len(ls) > 0:
            with open('black_tm.txt', 'r+') as b_tm:
                b_tm.write(f'{amz_brand}\n')
            return 'TM'
        else:
            return 'NO TM'

def title_transform(amz_title, brand=''):
    black_list = [brand, 'new', 'for', 'fits', 'free', 'shipping', "with", "and", "the", "of", "in", "\'", '\"', '(', ')']
    amz_title = amz_title.split(' ')
    new_title = [x.lower() for x in amz_title if x not in black_list]
    amz_title = OrderedSet(new_title)
    title = '+'.join(amz_title)
    return title
