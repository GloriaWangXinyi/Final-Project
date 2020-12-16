#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import requests
import secrets
import sqlite3
#from bs4 import BeautifulSoup
import os
import pandas as pd
import numpy as np
import plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import webbrowser as web

API_key = secrets.API_Key

py.offline.init_notebook_mode(connected = True)  

def restaurants_of_city(city):

    baseurl = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': 'bearer %s' % API_key}
    params = {'location':city} 
    response = requests.get(baseurl, params=params, headers=headers)
    results = response.json()['businesses']

    restaurant_list = []
    restaurant_dict = {}
    for r in results:
        restaurant_dict['name'] = r['name']
        restaurant_dict['review_count'] = r['review_count']
        restaurant_dict['rating'] = r['rating']
        restaurant_dict['price'] = r['price']
        restaurant_dict['url'] = r['url']
        categories = r['categories']
        category_list = []
        for c in categories:
            category_list.append(c['title'])
        restaurant_dict['category'] = category_list
        restaurant_dict['state'] = r['location']['state']
        restaurant_dict['city'] = r['location']['city']
        restaurant_list.append(restaurant_dict.copy())
    
    return restaurant_list


#def build_restaurant_dict(url):
    #response = requests.get(url)
    #print(response.text)
    #soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup)
    #searching_div = soup.find_all('div', id='wrap')
    #s1 = soup.find_all('div', attrs={'class':'main-content-wrap main-content-wrap--full'})
    #print(s1)
    #searching_div = soup.find_all('div', class_="lemon--div__373c0__1mboc i-stars__373c0__1T6rz i-stars--large-4__373c0__1d6HV border-color--default__373c0__3-ifU overflow--hidden__373c0__2y4YK")
    
    #rating = searching_div.find['aria-label']
    #print(rating)


def write_database(restaurant_list, db_name):

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    drop_query = 'DROP TABLE IF EXISTS "restaurant"'
    create_query = '''
        CREATE TABLE IF NOT EXISTS "restaurant"(
            "name" TEXT,
            "review_count" INTEGER,
            "rating" NUMERIC,
            "price" TEXT,
            "category" TEXT,
            "state" TEXT,
            "city" TEXT
        )
    '''

    cursor.execute(drop_query)
    cursor.execute(create_query)
    connection.commit()

    for r in restaurant_list:
        insert_query = '''
            INSERT INTO restaurant
            VALUES (?,?,?,?,?,?,?)
        '''
        category_str = ', '.join(r['category'])
        value = [r['name'],r['review_count'],r['rating'],r['price'],category_str,r['state'],r['city']]

        cursor.execute(insert_query,value)
        connection.commit()
    

def food_category(food_string,db_name):

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    query = "SELECT * FROM restaurant GROUP BY category HAVING category LIKE ?"
    result = cursor.execute(query,('%'+food_string+'%',)).fetchall()
    connection.close()

    connection = sqlite3.connect('food_kind.sqlite')
    cursor = connection.cursor()
    drop_query = 'DROP TABLE IF EXISTS "restaurant"'
    create_query = '''
        CREATE TABLE IF NOT EXISTS "restaurant"(
            "name" TEXT,
            "review_count" INTEGER,
            "rating" NUMERIC,
            "price" TEXT,
            "category" TEXT,
            "state" TEXT,
            "city" TEXT
        )
    '''

    cursor.execute(drop_query)
    cursor.execute(create_query)
    connection.commit()

    for r in result:
        insert_query = '''
            INSERT INTO restaurant
            VALUES (?,?,?,?,?,?,?)
        '''

        value = [r[0],r[1],r[2],r[3],r[4],r[5],r[6]]

        cursor.execute(insert_query,value)
        connection.commit()

    return result


def top_rating():

    connection = sqlite3.connect("food_kind.sqlite")
    cursor = connection.cursor()
    query = "SELECT name, rating, category FROM restaurant ORDER BY rating DESC LIMIT 10"
    result = cursor.execute(query).fetchall()
    connection.close()
    return result

def top_review():

    connection = sqlite3.connect("food_kind.sqlite")
    cursor = connection.cursor()
    query = "SELECT name, review_count,category FROM restaurant ORDER BY review_count DESC LIMIT 10"
    result = cursor.execute(query).fetchall()
    connection.close()
    return result


def make_bar_chart(rank_method, rank_list):

    restaurant_name = []
    rank_value = []
    i=1
    for l in rank_list:
        restaurant_name.append(l[0])
        rank_value.append(l[1])
        print(i,l[0],l[1],l[2])
        i +=1

    pyplot = py.offline.plot

    trade_basic = go.Bar(x =restaurant_name, y = rank_value)
    layout = go.Layout(title = rank_method, xaxis = dict(title = 'Restaurant Name'))
    figure_basic = go.Figure(data = [trade_basic], layout = layout)
    pyplot(figure_basic)

#1. Ask the user to input the city
city = input('Select the city you want to find the restaurant.')
restaurant_list = restaurants_of_city(city)
db_name = 'restaurant_info.sqlite'
write_database(restaurant_list,db_name)

#2. Ask the user to input the food category (i.e. Burgers, Mexcian) he want to explore
food = input('What kinds of food you want to explore (i.e. Burgers, Mexican), press space if you don\'t want to specify?')
food_category(food,db_name)

#3. Ask the user to input the rank method (by rating or review count)
rank_method = input('Do you want to rank the restaurants by rating or review count?')
if rank_method == 'rating':
    result = top_rating()
else:
    result = top_review()
make_bar_chart(rank_method,result)

#4. Ask the user to select a restaurant for more information
while True:
    i = int(input('Select the restaurant number for more information.'))
    if i > len(result) or i<1:
        print('Please type in a valid number.')
    else:
        name = result[i-1][0]
        for dic in restaurant_list:
            if dic['name'] == name:
                url = dic['url']
                web.open(url)
        break