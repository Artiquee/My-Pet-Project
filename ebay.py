import re
import sys

import requests
from bs4 import BeautifulSoup


class EbayItemsList:

    # TODO Make better and scrape all data from page
    def ebay_items(self, s):
        ebay_url = str(
            f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={s}&_sacat=0&LH_TitleDesc=1&_sop=15&_stpos=10001&_fcid=1&rt=nc&LH_PrefLoc=3')

        try:
            page = requests.get(ebay_url, timeout=10)
        except requests.exceptions.ConnectionError:
            print("Connection refused")
            requests.status_code = "Connection refused"

        soup = BeautifulSoup(page.text, 'html.parser')

        ebay_items = soup.find_all('div', {'class': 's-item__info clearfix'})
        prices, links, titles, ratings, ratings_percent, ebay_shippings = ([] for i in range(6))
        for x in ebay_items[1:]:
            # Ebay items prices & shipping
            try:
                price = x.find('span', {'class': 's-item__price'}).text
            except:
                price = x.find('span', {'itemprop': 'price'}).text
            if 'Tap' in price:
                price = x.find('span', {'class': 'STRIKETHROUGH'}).text
            price = price.replace(',', '')
            price = price.split(' ')
            price = float(price[0].replace('$', ''))
            try:
                ebay_shipping = x.find('span', {'class': 's-item__shipping s-item__logisticsCost'}).text
            except:
                try:
                    ebay_shipping = x.find('span', {'class': 'POSITIVE BOLD'}).text
                except:
                    ebay_shipping = 0

            if ebay_shipping == None:
                ebay_shipping = x.find('span', {'class': 'POSITIVE BOLD'})
            if ebay_shipping != 0 and 'Free' in ebay_shipping:
                ebay_shipping = 0
            else:
                try:
                    ebay_shipping = float(
                        ''.join([i for i in ebay_shipping if i not in ['+', '$', 's', 'h', 'i', 'p', 'n', 'g']]))
                except:
                    ebay_shipping = 0
            total_price = price + ebay_shipping
            prices.append(total_price)
            # Ebay item titles
            titles.append(x.find('div', {'class': 's-item__title'}).text)

            # Ebay items link
            link = x.find(href=re.compile('ebay.com/itm/'), class_='s-item__link')['href']
            l = link.split('?')
            links.append(l[0])

            # Ebay ratings percent and score
            try:
                rating_ebay = x.find('span', {'class': 's-item__seller-info-text'}).text
            except:
                rating_ebay = 'null (0) 0'
            item_rating = str(re.findall(r"\((.*?)\)", rating_ebay))
            item_rating = ''.join([i for i in item_rating if i not in ['[', ']', "'", ","]])
            try:
                item_rating = int(item_rating)
            except:
                item_rating = item_rating.split(' ')
                item_rating = item_rating[1]
            ratings.append(item_rating)

            item_rating_percent = str(re.findall(r"\d+(?:,\d+)*(?:\.\d+)?%", rating_ebay))
            item_rating_percent = ''.join([i for i in item_rating_percent if i not in ['[', ']', "'", ",", '%']])
            if item_rating_percent == '':
                item_rating_percent = 0
            ratings_percent.append(item_rating_percent)

        return {titles[i]: (links[i], float(prices[i]), float(ratings_percent[i]), int(ratings[i])) for i in
                range(len(titles))}

# =====================================================================================================================
