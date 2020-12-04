from requests_oauthlib import OAuth1
import requests
import secrets
from bs4 import BeautifulSoup

API_key = secrets.API_Key

def restaurants_of_city(city):

    baseurl = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'bearer %s' % API_key}
    params = {'location':city} 
    response = requests.get(baseurl, params=params, headers=headers)
    results = response.json()['businesses']

    restaurant_dict = {}
    for r in results:
        restaurant_dict['name'] = r['name']
        restaurant_dict['url'] = r['url']
    
    return restaurant_dict


def build_restaurant_dict(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    #searching_div = soup.find_all('div', id='wrap')
    s1 = soup.find_all('div', class_=('lemon--div__373c0__1mboc','arrange-unit__373c0__o3tjT','arrange-unit-fill__373c0__3Sfw1','border-color--default__373c0__3-ifU'))
    #searching_div = soup.find_all('div', class_="lemon--div__373c0__1mboc i-stars__373c0__1T6rz i-stars--large-4__373c0__1d6HV border-color--default__373c0__3-ifU overflow--hidden__373c0__2y4YK")
    print(s1)
    #rating = searching_div.find['aria-label']
    #print(rating)

build_restaurant_dict('https://www.yelp.com/biz/four-barrel-coffee-san-francisco')