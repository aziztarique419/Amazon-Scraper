import requests
from urllib.request import Request, urlopen as uReq
from bs4 import BeautifulSoup as bs
import pandas as pd
import random

user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15"
]

def get_random_user_agent():
    return random.choice(user_agents)

def scrape_amazon(query):
    query = query.strip().replace(" ", "+")
    url = f"https://www.amazon.in/s?k={query}&crid=2VBRNOJAK0OLN&sprefix={query}%2Caps%2C264&ref=nb_sb_noss_1"
    header = {"User-Agent": get_random_user_agent()}
    
    try:
        request = Request(url, headers=header)
        link = uReq(request)
        firstlink = link.read()
        link.close()
        amazon_html = bs(firstlink, "html.parser")
        elems = amazon_html.findAll("div", {"class": "sg-col-inner"})
        title = elems[10].div.div.h2.get_text()
        link = elems[10].div.div.h2.a["href"]
        price = elems[10].find("span",{"class":"a-price-whole"}).get_text()
        product_link = "https://www.amazon.in" + link
    except Exception as e:
        print(f"Error during initial request or parsing: {e}")
        return {}, pd.DataFrame()

    l_product_url = []
    for elem in elems:
        try:
            u = elem.div.div.a['href']
            product_url = "https://www.amazon.in" + u
            l_product_url.append(product_url)
        except Exception as e:
            print(f"Error extracting product URL: {e}")
            continue


    try:
        next_request = Request(l_product_url[10], headers=header)
        op = uReq(next_request)
        reading = op.read()
        op.close()
        beautify_reading = bs(reading, 'html.parser')
        d = beautify_reading.findAll('div', {'class': 'card-padding'})
    except Exception as e:
        print(f"try with different product please")
        return {}, pd.DataFrame()

    rating = []
    review_title = []
    review_content = []

    for i in d:
        try:
            a = i.findAll('a', {'data-hook': 'review-title'})
            b = i.findAll('span', {'data-hook': 'review-body'})
            for j in a:
                s = j.get_text()
                r = s.split("\n")
                rating.append(r[0])
                review_title.append(r[1])
            for k in b:
                t = k.get_text()
                q = t.split('Read more')
                if len(q[0]) > 200:
                    review_content.append(q[0][1:len(q[0])-1])
                else:
                    review_content.append(q[0][1:len(q[0])-1])
        except Exception as e:
            print(f"check any other product")
            continue

    product_info = {
        'title': title,
        'price': price,
        'link': product_link
    }

    df = pd.DataFrame({'rating': rating, 'title': review_title, 'content': review_content})
    
    return product_info, df
