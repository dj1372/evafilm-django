import string
import sys
import urllib.parse
from django.shortcuts import render
from os import error, name, stat
from django.contrib.auth.decorators import user_passes_test
from django import forms
from django.shortcuts import render
import requests
from requests import exceptions
from requests.api import get, head
from requests.models import HTTPError
from movies.models import PlayList, Actor, Season, Director, Episode, Country, Category
from .forms import GetLinkForm
from .forms import GetMultiLinkForm
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from PIL import Image
from sys import exit
from urllib.parse import urlparse
import re
import os
import time
import datetime
import random
import io

from django.contrib.auth import get_user_model

User = get_user_model()


ip_addresses = [
    'http://mrrsgusd:odp5frtaq8nj@209.127.191.180:9279',
    'http://mrrsgusd:odp5frtaq8nj@193.8.56.119:9183',
    'http://mrrsgusd:odp5frtaq8nj@45.95.99.226:7786'
]


def get_message(msg):
    with io.open('log.txt', 'a', encoding="utf-8") as logfile:
        logfile.write(str(msg) + '\n\n')


def to_url(name):
    name = name.replace(' ', '-')
    name = name.lower()
    return name


def to_high(source):
    source = source.split('V1_')
    source = source[0] + 'V1_.jpg'
    return source


def single_scraper(url):
    get_message('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~    ' + str(datetime.datetime.now()) +
                '    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n                                LOGGING STARTED\n')
    movie_data = {
        'movie_details': [],
        'actor_details': [],
        'dir_details': [],
    }

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    main_url = 'https://www.imdb.com'
    get_message('Sending request to : ' + url)

    proxy_index = random.randint(0, len(ip_addresses) - 1)
    proxy = {"http": ip_addresses[proxy_index], "https": ip_addresses[proxy_index]}
    """try:
        r = requests.get(url, headers=headers, timeout=10, proxies=proxy)
        get_message('Using : ' + proxy)
    except:
        r = requests.get(url, headers=headers, timeout=10)
        get_message('Normal request')"""

    get_message('Using : ' + str(proxy))
    r = requests.get(url, headers=headers)
    time.sleep(10.4)
    if r.status_code != 200:
        get_message('Response status: ' + str(r.status_code))
    else:
        get_message('Response status: ' + str(r.status_code) + '\n')
        print(r.status_code)

        soup = BeautifulSoup(r.text, 'lxml')

        try:
            title = soup.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0').text
        except:
            get_message('Title not found')
            title = None

        try:
            m = PlayList.objects.get(name_en=title)
            get_message('Movie already exists')
            return None
        except:
            try:
                type_parent = soup.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-4')
                content_type = type_parent.find_all('li', role='presentation')[0].text
            except:
                type_parent = '___type_parent___notfound__-'
                get_message('Type not found')
                content_type = 'TV Series'
            try:
                if content_type == 'TV Series':
                    film_type = 2
                    dur = ' '
                    get_message('Type = ' + film_type)
                else:
                    film_type = 1
                    try:
                        dur_parent = soup.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-4')
                        duration = dur_parent.find_all('li', role='presentation')[2].text
                        try:
                            dur = duration.replace("h", " ساعت و ")
                            dur = dur.replace("min", " دقیقه  ")
                        except:
                            dur = duration
                    except:
                        dur = ' '
                        Exception('time not found')

            except:
                get_message('Could not set Type for this object')
                film_type = 1
                dur = ' '

            get_message('Fetching actor data')

            i = 0
            while i < 5:
                try:
                    actor_url = soup.find_all('a', class_='StyledComponents__ActorName-y9ygcu-1')[i].get('href')
                    r_actor = requests.get(main_url + actor_url, headers=headers).text
                    soup_actor = BeautifulSoup(r_actor, 'lxml')
                    actor_name = soup_actor.find('span', class_='itemprop').text
                    actor_bio = soup_actor.find('div', class_='inline').text
                    movie_data['actor_details'].append({'name': actor_name, 'summary': actor_bio})
                    get_message('Successfully fetched actor ' + str(i))
                    i += 1
                    try:
                        l_actor_pic = soup_actor.find('img', id='name-poster').get('src')
                        l_actor_pic_r = requests.get(l_actor_pic, headers=headers)
                        l_actor_img = Image.open(BytesIO(l_actor_pic_r.content))
                        l_actor_img.save('media/' + to_url(actor_name) + '.jpg')
                        get_message('Successfully saved actor image')
                    except:
                        get_message('Actor image not found')
                except:
                    get_message('Actor URL not found')
                    actor_name = ' '
                    actor_bio = ' '
                get_message('Fetching actor images')

            #        with open('log.txt', 'a') as logfile:
            #           logfile.write('start actor_pic = soup_actor.find line 155 \n')
            #        try:
            #            actor_pic = soup_actor.find('img', id='name-poster').get('src')
            #            # actor_pic_r = requests.get(to_high(actor_pic))
            #            #actor_img = Image.open(BytesIO(actor_pic.content))
            #            # actor_img.save('/home/ubuntu/scraper/actors/' + to_url(actor_name) + '.webp')
            #        except:
            #            print('actor_pic not found')
            #            actor_pic = Image.open('/home/ubuntu/evafilm/avatar.jpg')
            #            with open('log.txt', 'a') as logfile:
            #                logfile.write('this happen because Actor image not found line 127\n')
            #            actor_img = actor_pic
            #
            #        with open('log.txt', 'a') as logfile:
            #            logfile.write('end actor_pic = soup_actor.find line 169 \n')

            try:
                year = str(soup.find_all('span', class_='jedhex')[0].text)
                get_message('Successfully found Year')

            except:
                year = '0000'
                get_message('Could not find Year')

            # High quality image
            """get_message('~~~~~~~~~~~~~~~~~~~~~~~~   Fetching High Quality Image   ~~~~~~~~~~~~~~~~~~~~~~~~ ')
            try:
                image_url = soup.find('a', class_='ipc-lockup-overlay').get('href')
                img_r = requests.get('https://www.imdb.com' + image_url, headers=headers, timeout=30).text
                img_soup = BeautifulSoup(img_r, 'lxml')
                img_url = img_soup.find('img', class_='MediaViewerImagestyles__PortraitImage-sc-1qk433p-0').get('src')
                img_obj = requests.get(img_url,  headers=headers, timeout=30)
                img = Image.open(BytesIO(img_obj.content))
                img_title = to_url(title)
                img.save('/home/ubuntu/scraper/movies/' + img_title + '.webp')
                get_message('~~~~~~~~~~~ Successfully downloaded High Quality Image ~~~~~~~~~~~~~~~~')
            except requests.Timeout as e:
                get_message('High quality image request timed out')"""

            get_message('Fetching Low Quality Image')
            try:
                l_image_url = soup.find('img', class_='ipc-image').get('src')
                l_img_obj = requests.get(l_image_url, headers=headers)
                l_img = Image.open(BytesIO(l_img_obj.content))
                l_img_title = to_url(title)
                l_img.save('media/' + l_img_title + '.jpg')
            except:
                get_message('Low quality image failed')

            try:
                tv_pg = soup.find_all('span', class_='jedhex')[1].text
                if tv_pg == 'R':
                    tv_pg == 17
                elif tv_pg == 'pg-13':
                    tv_pg = 13
                elif tv_pg == 'pg':
                    tv_pg = 7
                else:
                    tv_pg = 17
            except:
                get_message('TV-PG failed')
                tv_pg = 'R'

            try:
                rating = soup.find('span', class_='fhMjqK').text
            except:
                get_message('Rating not found')
                rating = 0
            try:
                summary = soup.find('span', class_="GenresAndPlot__TextContainerBreakpointXL-cum89p-4").text
                summary = summary.strip()
            except:
                summary = ' '
                get_message('Summary not found')

            try:
                director1 = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')[0].get('href')
                r_dir = requests.get(main_url + director1, headers=headers).text
                dir_soup = BeautifulSoup(r_dir, 'lxml')
                dir_name = dir_soup.find('span', class_='itemprop').text
                dir_bio = dir_soup.find('div', class_='inline').text
                movie_data['dir_details'].append({'name': dir_name, 'summary': dir_bio})
                """get_message('Fetching Director High Q image')
                try:
                    dir_pic = dir_soup.find('img', id='name-poster').get('src')
                    dir_pic_r = requests.get(to_high(dir_pic))
                    dir_img = Image.open(BytesIO(dir_pic_r.content))
                    os.mkdir('/home/ubuntu/scraper/' + title + '/directors')
                    dir_img.save('/home/ubuntu/scraper/directors/' + to_url(dir_name) + '.webp')
                except requests.Timeout as e:
                    get_message('Director High Q Image failed')"""

                try:
                    l_dir_pic = dir_soup.find('img', id='name-poster').get('src')
                    l_dir_pic_r = requests.get(l_dir_pic, headers=headers)
                    l_dir_img = Image.open(BytesIO(l_dir_pic_r.content))
                    l_dir_img.save('media/' + to_url(dir_name) + '.jpg')
                    get_message('Director Low Q Image fetched')
                except:
                    get_message('Director Low Q Image failed')
                # comment
                get_message('Fetching 2nd Director')
                try:
                    director2 = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')[1].get('href')
                    r_dir2 = requests.get(main_url + director2, headers=headers).text
                    dir2_soup = BeautifulSoup(r_dir2, 'lxml')
                    dir2_name = dir_soup.find('span', class_='itemprop').text
                    dir2_bio = soup_actor.find('div', class_='inline').text
                    movie_data['dir_details'].append({'name': dir2_name, 'summary': dir2_bio})
                    """try:
                        dir2_pic = dir2_soup.find('img', id='name-poster').get('src')
                        dir2_pic_r = requests.get(to_high(dir2_pic))
                        dir2_img = Image.open(BytesIO(dir2_pic_r.content))
                        dir2_img.save('/home/ubuntu/scraper/directors/' + to_url(dir2_name) + '.webp')
                    except:
                        get_message('Director 2 High Q pic failed')"""
                    try:
                        l_dir2_pic = dir2_soup.find('img', id='name-poster').get('src')
                        l_dir2_pic_r = requests.get(l_dir2_pic, headers=headers)
                        l_dir2_img = Image.open(BytesIO(l_dir2_pic_r.content))
                        l_dir2_img.save('media/' + to_url(dir2_name) + '.jpg')
                    except:
                        get_message('Director 2 Low Q pic failed')
                except:
                    director2 = ' '
                    Exception('No 2nd director')
            except:
                director1 = ' '
                Exception('No director')
            with open('log.txt', 'a') as logfile:
                logfile.write('line 274\n')

            get_message('~~~~~~~~~~~~  Fetching Genres ~~~~~~~~~~~~~')
            try:
                category1 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[0].text
                genre1 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[0].text

                if genre1 == 'Action':
                    genre1 = 1
                elif genre1 == 'Comedy':
                    genre1 = 5
                elif genre1 == 'Family':
                    genre1 = 9
                elif genre1 == 'History':
                    genre1 = 13
                elif genre1 == 'Mystery':
                    genre1 = 17
                elif genre1 == 'Sci-Fi':
                    genre1 = 21
                elif genre1 == 'War':
                    genre1 = 25
                elif genre1 == 'Adventure':
                    genre1 = 2
                elif genre1 == 'Crime':
                    genre1 = 6
                elif genre1 == 'Fantasy':
                    genre1 = 10
                elif genre1 == 'Horror':
                    genre1 = 14
                elif genre1 == 'News':
                    genre1 = 18
                elif genre1 == 'Sport':
                    genre1 = 22
                elif genre1 == 'Western':
                    genre1 = 26
                elif genre1 == 'Animation':
                    genre1 = 3
                elif genre1 == 'Documentary':
                    genre1 = 7
                elif genre1 == 'Biography':
                    genre1 = 4
                elif genre1 == 'Musical':
                    genre1 = 15
                elif genre1 == 'Drama':
                    genre1 = 8
                elif genre1 == 'Thriller':
                    genre1 = 24
                elif genre1 == 'Romance':
                    genre1 = 20
                elif genre1 == 'Film-Noir':
                    genre1 = 11
                else:
                    genre1 = None
            except:
                genre1 = None
                category1 = None
                Exception('Could not set genre 1')

            try:
                category2 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[1].text
                genre2 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[1].text
                get_message('Fetched Genre 2')

                try:
                    if genre2 == 'Action':
                        genre2 = 1
                    elif genre2 == 'Comedy':
                        genre2 = 5
                    elif genre2 == 'Family':
                        genre2 = 9
                    elif genre2 == 'History':
                        genre2 = 13
                    elif genre2 == 'Mystery':
                        genre2 = 17
                    elif genre2 == 'Sci-Fi':
                        genre2 = 21
                    elif genre2 == 'War':
                        genre2 = 25
                    elif genre2 == 'Adventure':
                        genre2 = 2
                    elif genre2 == 'Crime':
                        genre2 = 6
                    elif genre2 == 'Fantasy':
                        genre2 = 10
                    elif genre2 == 'Horror':
                        genre2 = 14
                    elif genre2 == 'News':
                        genre2 = 18
                    elif genre2 == 'Sport':
                        genre2 = 22
                    elif genre2 == 'Western':
                        genre2 = 26
                    elif genre2 == 'Animation':
                        genre2 = 3
                    elif genre2 == 'Documentary':
                        genre2 = 7
                    elif genre2 == 'Biography':
                        genre2 = 4
                    elif genre2 == 'Musical':
                        genre2 = 15
                    elif genre2 == 'Drama':
                        genre2 = 8
                    elif genre2 == 'Thriller':
                        genre2 = 24
                    elif genre2 == 'Romance':
                        genre2 = 20
                    elif genre2 == 'Film-Noir':
                        genre2 = 11
                    else:
                        genre1 = None
                except:
                    genre2 = None
                    Exception('Could not set genre')

            except:
                category2 = None
                genre2 = None
                Exception('Genre 2 not found')

            try:
                category3 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[2].text
                genre3 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[2].text
                get_message('Fetched Genre 3')
                try:
                    if genre3 == 'Action':
                        genre3 = 1
                    elif genre3 == 'Comedy':
                        genre3 = 5
                    elif genre3 == 'Family':
                        genre3 = 9
                    elif genre3 == 'History':
                        genre3 = 13
                    elif genre3 == 'Mystery':
                        genre3 = 17
                    elif genre3 == 'Sci-Fi':
                        genre3 = 21
                    elif genre3 == 'War':
                        genre3 = 25
                    elif genre3 == 'Adventure':
                        genre3 = 2
                    elif genre3 == 'Crime':
                        genre3 = 6
                    elif genre3 == 'Fantasy':
                        genre3 = 10
                    elif genre3 == 'Horror':
                        genre3 = 14
                    elif genre3 == 'News':
                        genre3 = 18
                    elif genre3 == 'Sport':
                        genre3 = 22
                    elif genre3 == 'Western':
                        genre3 = 26
                    elif genre3 == 'Animation':
                        genre3 = 3
                    elif genre3 == 'Documentary':
                        genre3 = 7
                    elif genre3 == 'Biography':
                        genre3 = 4
                    elif genre3 == 'Musical':
                        genre3 = 15
                    elif genre3 == 'Drama':
                        genre3 = 8
                    elif genre3 == 'Thriller':
                        genre3 = 24
                    elif genre3 == 'Romance':
                        genre3 = 20
                    elif genre3 == 'Film-Noir':
                        genre3 = 11
                    else:
                        genre1 = None
                except:
                    genre3 = None
                    Exception('Could not set genre')

            except:
                genre3 = None
                category3 = None
                Exception('Genre 3 not found')

            try:
                category4 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[3].text
                genre4 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[3].text
                get_message('Fetched Genre 4')
                try:
                    if genre4 == 'Action':
                        genre4 = 1
                    elif genre4 == 'Comedy':
                        genre4 = 5
                    elif genre4 == 'Family':
                        genre4 = 9
                    elif genre4 == 'History':
                        genre4 = 13
                    elif genre4 == 'Mystery':
                        genre4 = 17
                    elif genre4 == 'Sci-Fi':
                        genre4 = 21
                    elif genre4 == 'War':
                        genre4 = 25
                    elif genre4 == 'Adventure':
                        genre4 = 2
                    elif genre4 == 'Crime':
                        genre4 = 6
                    elif genre4 == 'Fantasy':
                        genre4 = 10
                    elif genre4 == 'Horror':
                        genre4 = 14
                    elif genre4 == 'News':
                        genre4 = 18
                    elif genre4 == 'Sport':
                        genre4 = 22
                    elif genre4 == 'Western':
                        genre4 = 26
                    elif genre4 == 'Animation':
                        genre4 = 3
                    elif genre4 == 'Documentary':
                        genre4 = 7
                    elif genre4 == 'Biography':
                        genre4 = 4
                    elif genre4 == 'Musical':
                        genre4 = 15
                    elif genre4 == 'Drama':
                        genre4 = 8
                    elif genre4 == 'Thriller':
                        genre4 = 24
                    elif genre4 == 'Romance':
                        genre4 = 20
                    elif genre4 == 'Film-Noir':
                        genre4 = 11
                    else:
                        genre1 = None
                except:
                    genre4 = None
                    Exception('Could not set genre')

            except:
                category4 = None
                genre4 = None
                Exception('Genre 4 not found')

            get_message('Fetching Trailer URL')
            try:
                trailer = soup.find('a', class_='hero-media__slate-overlay').get('href')
                trailer = main_url + trailer
            except:
                trailer = ' '
            try:
                users_view = soup.find('div', class_='AggregateRatingButton__TotalRatingAmount-sc-1il8omz-3').text
                users_view = re.sub('\D', '', users_view)
            except:
                users_view = '0'
                get_message('user view not found')
            """if 'M' in users_view:
                users_view = users_view.replace('M', ' میلون نفر ')
            elif 'K' in users_view:
                users_view = users_view.replace('K', ' هزار نفر ')
            else:
                users_view = users_view"""
            try:
                c = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item')
            except:
                get_message('Country not found')
            get_message('Fetcing Country...')
            for child in c:
                if 'country' in child.get('href'):
                    country = child.text
                    if country == 'United States':
                        country = 'آمریکا'
                    elif country == 'United Kingdom':
                        country = 'انگلیس'
                    elif country == 'France':
                        country = 'فرانسه'
                    elif country == 'India':
                        country = 'هند'
                    elif country == 'Canada':
                        country = 'کانادا'
                    elif country == 'Hong Kong':
                        country = 'هنگ کنک'
                    elif country == 'South Korea':
                        country = 'کره جنوبی'
                    elif country == 'Mexico':
                        country = 'مکزیک'
                    else:
                        country = 'آمریکا'
                else:
                    country = 'آمریکا'

                movie_data['movie_details'].append(
                    {'title': title, 'summary': summary, 'country': country, 'rating': float(rating),
                     'user_views': float(users_view),
                     'year': year, 'time': dur, 'tv_pg': tv_pg, 'trailer_url': trailer, 'category1': genre1,
                     'category2': genre2,
                     'category3': genre3, 'category4': genre4})
                get_message('End of the Scraping')

                return movie_data, category1, category2, category3, category4, film_type


def multiple_scraper(multi_url):
    movie_data = {
        'movie_1': {
            'movie_details': [],
            'actors': [],
            'directors': []
        },
        'movie_2': {
            'movie_details': [],
            'actors': [],
            'directors': []
        },
        'movie_3': {
            'movie_details': [],
            'actors': [],
            'directors': []
        }
    }

    delay = random.uniform(14.2, 18.4)
    delay = str(delay)[:4]
    delay = float(delay)
    get_message('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~    ' + str(datetime.datetime.now()) +
                '    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n                                Multi scraping\n')

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}

    r = requests.get(multi_url, headers=headers)
    get_message('Multi scraper using normal request')

    time.sleep(delay)

    soup = BeautifulSoup(r.text, 'lxml')

    movie_list = []
    movie_url = soup.find_all('h3', class_='lister-item-header')
    for url in movie_url:
        movie_list.append(url)

    i = 0
    mov_i = 1
    act_i = 1

    for movie in movie_list:
        get_message(str(mov_i) + 'movie')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        main_url = 'https://www.imdb.com'

        link = movie.find('a').get('href')
        check_name = movie.find('a').text
        get_message('link = ' + main_url + link)
        get_message('name checker : ' + check_name)

        # get_message('Link = ' + main_url + link)
        """try:
            proxy_index = random.randint(0, len(ip_addresses) - 1)
            proxy = {"http": ip_addresses[proxy_index], "https": ip_addresses[proxy_index]}
            r_multi = requests.get(main_url + link, headers=headers, timeout=10, proxies=proxy)
            get_message('Using proxy')
        except:
            r_multi = requests.get(main_url + link, headers=headers, timeout=10)"""

        if PlayList.objects.filter(name_en=check_name).exists():
            get_message(check_name + ' Already exists')
            time.sleep(1)
            continue
        elif len(movie_data['movie_3']['movie_details']) == 1:
            get_message('Appended ' + str(len(movie_data)) + ' movies')
            get_message('\n\n\n\n' + str(movie_data))
            break
        else:
            r_multi = requests.get(main_url + link, headers=headers)
            time.sleep(delay)
            if r_multi.status_code != 200:
                get_message('Response status not 200: ' + str(r_multi.status_code))
            else:
                get_message('Response status: ' + str(r_multi.status_code) + '\n')
                soup_m = BeautifulSoup(r_multi.text, 'lxml')

                try:
                    title = soup_m.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0').text
                except:
                    get_message('Title not found')
                try:
                    m = PlayList.objects.get(name_en=title)
                    i += 1
                    get_message('Movie Already Exists')
                    continue
                except:
                    try:
                        type_parent = soup_m.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-4')
                        content_type = type_parent.find_all('li', role='presentation')[0].text
                    except:
                        type_parent = ' '
                        get_message('Type not found')
                        content_type = 'TV Series'
                    try:
                        if content_type == 'TV Series':
                            film_type = 2
                            dur = ' '
                            get_message('Type = ' + film_type)
                        else:
                            film_type = 1
                            try:
                                dur_parent = soup_m.find('div',
                                                         class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-4')
                                duration = dur_parent.find_all('li', role='presentation')[2].text
                                try:
                                    dur = duration.replace("h", " ساعت و ")
                                    dur = dur.replace("min", " دقیقه  ")
                                except:
                                    dur = duration
                            except:
                                dur = ' '
                                Exception('time not found')

                    except:
                        film_type = 1
                        get_message('Film Type : ' + str(film_type))
                        dur = ' '

                    get_message('Fetching actor data')

                    i = 0
                    while i < 5:
                        get_message('Fetching actor ' + str(i + 1))
                        actor_url = soup_m.find_all('a', class_='StyledComponents__ActorName-y9ygcu-1')[i].get('href')
                        r_actor = requests.get(main_url + actor_url, headers=headers).text
                        time.sleep(delay)
                        soup_actor = BeautifulSoup(r_actor, 'lxml')
                        actor_name = soup_actor.find('span', class_='itemprop').text
                        actor_bio = soup_actor.find('div', class_='inline').text
                        movie_data['movie_' + str(act_i)]['actors'].append({'name': actor_name, 'summary': actor_bio})
                        get_message('Successfully fetched actor ' + str(i))
                        try:
                            l_actor_pic = soup_actor.find('img', id='name-poster').get('src')
                            l_actor_pic_r = requests.get(l_actor_pic, headers=headers)
                            l_actor_img = Image.open(BytesIO(l_actor_pic_r.content))
                            l_actor_img.save('media/' + to_url(actor_name) + '.jpg')
                            get_message('Successfully saved actor image')
                        except:
                            get_message('Actor image not found')
                            l_actor_pic_r = l_actor_pic
                            l_actor_img = l_actor_pic_r
                        i += 1

                        # get_message('Actor URL not found')
                        # actor_name = ' '
                        # actor_bio = ' '
                        # get_message('Fetching actor images')

                    #        with open('log.txt', 'a') as logfile:
                    #           logfile.write('start actor_pic = soup_actor.find line 155 \n')
                    #        try:
                    #            actor_pic = soup_actor.find('img', id='name-poster').get('src')
                    #            # actor_pic_r = requests.get(to_high(actor_pic))
                    #            #actor_img = Image.open(BytesIO(actor_pic.content))
                    #            # actor_img.save('/home/ubuntu/scraper/actors/' + to_url(actor_name) + '.webp')
                    #        except:
                    #            print('actor_pic not found')
                    #            actor_pic = Image.open('/home/ubuntu/evafilm/avatar.jpg')
                    #            with open('log.txt', 'a') as logfile:
                    #                logfile.write('this happen because Actor image not found line 127\n')
                    #            actor_img = actor_pic
                    #
                    #        with open('log.txt', 'a') as logfile:
                    #            logfile.write('end actor_pic = soup_actor.find line 169 \n')

                    try:
                        year = str(soup_m.find_all('span', class_='jedhex')[0].text)
                        get_message('Successfully found Year :' + str(year))

                    except:
                        year = '0000'
                        get_message('Could not find Year')

                    # High quality image
                    """get_message('~~~~~~~~~~~~~~~~~~~~~~~~   Fetching High Quality Image   ~~~~~~~~~~~~~~~~~~~~~~~~ ')
                    try:
                        image_url = soup.find('a', class_='ipc-lockup-overlay').get('href')
                        img_r = requests.get('https://www.imdb.com' + image_url, headers=headers, timeout=30).text
                        img_soup = BeautifulSoup(img_r, 'lxml')
                        img_url = img_soup.find('img', class_='MediaViewerImagestyles__PortraitImage-sc-1qk433p-0').get('src')
                        img_obj = requests.get(img_url,  headers=headers, timeout=30)
                        img = Image.open(BytesIO(img_obj.content))
                        img_title = to_url(title)
                        img.save('/home/ubuntu/scraper/movies/' + img_title + '.webp')
                        get_message('~~~~~~~~~~~ Successfully downloaded High Quality Image ~~~~~~~~~~~~~~~~')
                    except requests.Timeout as e:
                        get_message('High quality image request timed out')"""

                    get_message('Fetching Low Quality Image')
                    try:
                        l_image_url = soup_m.find('img', class_='ipc-image').get('src')
                        l_img_obj = requests.get(l_image_url, headers=headers)
                        l_img = Image.open(BytesIO(l_img_obj.content))
                        l_img_title = to_url(title)
                        l_img.save('media/' + l_img_title + '.jpg')
                    except:
                        get_message('Low quality image failed')

                    try:
                        tv_pg = soup_m.find_all('span', class_='jedhex')[1].text
                        if tv_pg == 'R':
                            tv_pg == 17
                        elif tv_pg == 'pg-13':
                            tv_pg = 13
                        elif tv_pg == 'pg':
                            tv_pg = 7
                        else:
                            tv_pg = 17
                    except:
                        get_message('TV-PG failed')
                        tv_pg = 'R'

                    try:
                        rating = soup_m.find('span', class_='fhMjqK').text
                    except:
                        get_message('Rating not found')
                        rating = 0
                    try:
                        summary = soup_m.find('span', class_="GenresAndPlot__TextContainerBreakpointXL-cum89p-4").text
                        summary = summary.strip()
                    except:
                        summary = ' '
                        get_message('Summary not found')

                    try:
                        director1 = soup_m.find_all('a', class_='ipc-metadata-list-item__list-content-item')[0].get(
                            'href')
                        r_dir = requests.get(main_url + director1, headers=headers).text
                        dir_soup = BeautifulSoup(r_dir, 'lxml')
                        dir_name = dir_soup.find('span', class_='itemprop').text
                        dir_bio = dir_soup.find('div', class_='inline').text
                        movie_data['movie_' + str(dir_i)]['directors'].append({'name': dir_name, 'summary': dir_bio})
                        """get_message('Fetching Director High Q image')
                        try:
                            dir_pic = dir_soup.find('img', id='name-poster').get('src')
                            dir_pic_r = requests.get(to_high(dir_pic))
                            dir_img = Image.open(BytesIO(dir_pic_r.content))
                            os.mkdir('/home/ubuntu/scraper/' + title + '/directors')
                            dir_img.save('/home/ubuntu/scraper/directors/' + to_url(dir_name) + '.webp')
                        except requests.Timeout as e:
                            get_message('Director High Q Image failed')"""

                        try:
                            l_dir_pic = dir_soup.find('img', id='name-poster').get('src')
                            l_dir_pic_r = requests.get(l_dir_pic, headers=headers)
                            l_dir_img = Image.open(BytesIO(l_dir_pic_r.content))
                            l_dir_img.save('media/' + to_url(dir_name) + '.jpg')
                            get_message('Director Low Q Image fetched')
                        except:
                            get_message('Director Low Q Image failed')

                        get_message('Fetching 2nd Director')
                        try:
                            director2 = soup_m.find_all('a', class_='ipc-metadata-list-item__list-content-item')[1].get(
                                'href')
                            r_dir2 = requests.get(main_url + director2, headers=headers).text
                            dir2_soup = BeautifulSoup(r_dir2, 'lxml')
                            dir2_name = dir_soup.find('span', class_='itemprop').text
                            dir2_bio = soup_actor.find('div', class_='inline').text
                            movie_data['movie_' + str(dir_i)]['directors'].append(
                                {'name': dir2_name, 'summary': dir2_bio})
                            """try:
                                dir2_pic = dir2_soup.find('img', id='name-poster').get('src')
                                dir2_pic_r = requests.get(to_high(dir2_pic))
                                dir2_img = Image.open(BytesIO(dir2_pic_r.content))
                                dir2_img.save('/home/ubuntu/scraper/directors/' + to_url(dir2_name) + '.webp')
                            except:
                                get_message('Director 2 High Q pic failed')"""
                            try:
                                l_dir2_pic = dir2_soup.find('img', id='name-poster').get('src')
                                l_dir2_pic_r = requests.get(l_dir2_pic, headers=headers)
                                l_dir2_img = Image.open(BytesIO(l_dir2_pic_r.content))
                                l_dir2_img.save('media/' + to_url(dir2_name) + '.jpg')
                            except:
                                get_message('Director 2 Low Q pic failed')
                        except:
                            director2 = ' '
                            Exception('No 2nd director')
                    except:
                        director1 = ' '
                        Exception('No director')
                    with open('log.txt', 'a') as logfile:
                        logfile.write('line 274\n')

                    get_message('~~~~~~~~~~~~  Fetching Genres ~~~~~~~~~~~~~')
                    try:
                        category1 = soup_m.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[0].text
                        genre1 = soup_m.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[0].text

                        if genre1 == 'Action':
                            genre1 = 1
                        elif genre1 == 'Comedy':
                            genre1 = 5
                        elif genre1 == 'Family':
                            genre1 = 9
                        elif genre1 == 'History':
                            genre1 = 13
                        elif genre1 == 'Mystery':
                            genre1 = 17
                        elif genre1 == 'Sci-Fi':
                            genre1 = 21
                        elif genre1 == 'War':
                            genre1 = 25
                        elif genre1 == 'Adventure':
                            genre1 = 2
                        elif genre1 == 'Crime':
                            genre1 = 6
                        elif genre1 == 'Fantasy':
                            genre1 = 10
                        elif genre1 == 'Horror':
                            genre1 = 14
                        elif genre1 == 'News':
                            genre1 = 18
                        elif genre1 == 'Sport':
                            genre1 = 22
                        elif genre1 == 'Western':
                            genre1 = 26
                        elif genre1 == 'Animation':
                            genre1 = 3
                        elif genre1 == 'Documentary':
                            genre1 = 7
                        elif genre1 == 'Biography':
                            genre1 = 4
                        elif genre1 == 'Musical':
                            genre1 = 15
                        elif genre1 == 'Drama':
                            genre1 = 8
                        elif genre1 == 'Thriller':
                            genre1 = 24
                        elif genre1 == 'Romance':
                            genre1 = 20
                        elif genre1 == 'Film-Noir':
                            genre1 = 11
                        else:
                            genre1 = None
                    except:
                        genre1 = None
                        category1 = None
                        Exception('Could not set genre 1')

                    try:
                        category2 = soup_m.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[1].text
                        genre2 = soup_m.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[1].text
                        get_message('Fetched Genre 2')

                        try:
                            if genre2 == 'Action':
                                genre2 = 1
                            elif genre2 == 'Comedy':
                                genre2 = 5
                            elif genre2 == 'Family':
                                genre2 = 9
                            elif genre2 == 'History':
                                genre2 = 13
                            elif genre2 == 'Mystery':
                                genre2 = 17
                            elif genre2 == 'Sci-Fi':
                                genre2 = 21
                            elif genre2 == 'War':
                                genre2 = 25
                            elif genre2 == 'Adventure':
                                genre2 = 2
                            elif genre2 == 'Crime':
                                genre2 = 6
                            elif genre2 == 'Fantasy':
                                genre2 = 10
                            elif genre2 == 'Horror':
                                genre2 = 14
                            elif genre2 == 'News':
                                genre2 = 18
                            elif genre2 == 'Sport':
                                genre2 = 22
                            elif genre2 == 'Western':
                                genre2 = 26
                            elif genre2 == 'Animation':
                                genre2 = 3
                            elif genre2 == 'Documentary':
                                genre2 = 7
                            elif genre2 == 'Biography':
                                genre2 = 4
                            elif genre2 == 'Musical':
                                genre2 = 15
                            elif genre2 == 'Drama':
                                genre2 = 8
                            elif genre2 == 'Thriller':
                                genre2 = 24
                            elif genre2 == 'Romance':
                                genre2 = 20
                            elif genre2 == 'Film-Noir':
                                genre2 = 11
                            else:
                                genre1 = None
                        except:
                            genre2 = None
                            Exception('Could not set genre')

                    except:
                        category2 = None
                        genre2 = None
                        Exception('Genre 2 not found')

                    try:
                        category3 = soup_m.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[2].text
                        genre3 = soup_m.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[2].text
                        get_message('Fetched Genre 3')
                        try:
                            if genre3 == 'Action':
                                genre3 = 1
                            elif genre3 == 'Comedy':
                                genre3 = 5
                            elif genre3 == 'Family':
                                genre3 = 9
                            elif genre3 == 'History':
                                genre3 = 13
                            elif genre3 == 'Mystery':
                                genre3 = 17
                            elif genre3 == 'Sci-Fi':
                                genre3 = 21
                            elif genre3 == 'War':
                                genre3 = 25
                            elif genre3 == 'Adventure':
                                genre3 = 2
                            elif genre3 == 'Crime':
                                genre3 = 6
                            elif genre3 == 'Fantasy':
                                genre3 = 10
                            elif genre3 == 'Horror':
                                genre3 = 14
                            elif genre3 == 'News':
                                genre3 = 18
                            elif genre3 == 'Sport':
                                genre3 = 22
                            elif genre3 == 'Western':
                                genre3 = 26
                            elif genre3 == 'Animation':
                                genre3 = 3
                            elif genre3 == 'Documentary':
                                genre3 = 7
                            elif genre3 == 'Biography':
                                genre3 = 4
                            elif genre3 == 'Musical':
                                genre3 = 15
                            elif genre3 == 'Drama':
                                genre3 = 8
                            elif genre3 == 'Thriller':
                                genre3 = 24
                            elif genre3 == 'Romance':
                                genre3 = 20
                            elif genre3 == 'Film-Noir':
                                genre3 = 11
                            else:
                                genre1 = None
                        except:
                            genre3 = None
                            Exception('Could not set genre')

                    except:
                        genre3 = None
                        category3 = None
                        Exception('Genre 3 not found')

                    try:
                        category4 = soup_m.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[3].text
                        genre4 = soup_m.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-5')[3].text
                        get_message('Fetched Genre 4')
                        try:
                            if genre4 == 'Action':
                                genre4 = 1
                            elif genre4 == 'Comedy':
                                genre4 = 5
                            elif genre4 == 'Family':
                                genre4 = 9
                            elif genre4 == 'History':
                                genre4 = 13
                            elif genre4 == 'Mystery':
                                genre4 = 17
                            elif genre4 == 'Sci-Fi':
                                genre4 = 21
                            elif genre4 == 'War':
                                genre4 = 25
                            elif genre4 == 'Adventure':
                                genre4 = 2
                            elif genre4 == 'Crime':
                                genre4 = 6
                            elif genre4 == 'Fantasy':
                                genre4 = 10
                            elif genre4 == 'Horror':
                                genre4 = 14
                            elif genre4 == 'News':
                                genre4 = 18
                            elif genre4 == 'Sport':
                                genre4 = 22
                            elif genre4 == 'Western':
                                genre4 = 26
                            elif genre4 == 'Animation':
                                genre4 = 3
                            elif genre4 == 'Documentary':
                                genre4 = 7
                            elif genre4 == 'Biography':
                                genre4 = 4
                            elif genre4 == 'Musical':
                                genre4 = 15
                            elif genre4 == 'Drama':
                                genre4 = 8
                            elif genre4 == 'Thriller':
                                genre4 = 24
                            elif genre4 == 'Romance':
                                genre4 = 20
                            elif genre4 == 'Film-Noir':
                                genre4 = 11
                            else:
                                genre1 = None
                        except:
                            genre4 = None
                            Exception('Could not set genre')

                    except:
                        category4 = None
                        genre4 = None
                        Exception('Genre 4 not found')

                    get_message('Fetching Trailer URL')
                    try:
                        trailer = soup_m.find('a', class_='hero-media__slate-overlay').get('href')
                        trailer = main_url + trailer
                    except:
                        get_message('Trailer not found')
                    try:
                        users_view = soup_m.find('div',
                                                 class_='AggregateRatingButton__TotalRatingAmount-sc-1il8omz-3').text
                        users_view = re.sub('\D', '', users_view)
                    except:
                        users_view = '0'
                        get_message('Users view not found')
                    """if 'M' in users_view:
                        users_view = users_view.replace('M', ' میلون نفر ')
                    elif 'K' in users_view:
                        users_view = users_view.replace('K', ' هزار نفر ')
                    else:
                        users_view = users_view"""
                    try:
                        c = soup_m.find_all('a', class_='ipc-metadata-list-item__list-content-item')
                    except:
                        c = ' '
                        get_message('Country not found. setting USA...')
                    get_message('Fetcing Country...')
                    for child in c:
                        if 'country' in child.get('href'):
                            country = child.text
                            if country == 'United States':
                                country = 'آمریکا'
                            elif country == 'United Kingdom':
                                country = 'انگلیس'
                            elif country == 'France':
                                country = 'فرانسه'
                            elif country == 'India':
                                country = 'هند'
                            elif country == 'Canada':
                                country = 'کانادا'
                            elif country == 'Hong Kong':
                                country = 'هنگ کنک'
                            elif country == 'South Korea':
                                country = 'کره جنوبی'
                            elif country == 'Mexico':
                                country = 'مکزیک'
                            else:
                                country = 'آمریکا'
                        else:
                            country = 'آمریکا'

                movie_data['movie_' + str(mov_i)]['movie_details'].append(
                    {'title': title, 'summary': summary, 'country': country, 'rating': float(rating),
                     'year': year, 'time': dur, 'tv_pg': tv_pg, 'category1': genre1,
                     'category2': genre2,
                     'category3': genre3, 'category4': genre4})

                get_message('End of the Scraping')
                get_message(movie_data)
                time.sleep(delay)
                mov_i += 1
                act_i += 1

    return movie_data, category1, category2, category3, category4, film_type


@user_passes_test(lambda u: u.is_superuser)
def MovieView(request):
    creator = User.objects.get(id=1)
    if request.method == 'POST':
        form = GetLinkForm(request.POST)
        form2 = GetMultiLinkForm(request.POST)
        if form.is_valid():
            movie_data, category1, category2, category3, category4, film_type = single_scraper(form.cleaned_data['url'])
            title = movie_data['movie_details'][0]['title']
            summary = movie_data['movie_details'][0]['summary']
            rating = movie_data['movie_details'][0]['rating']
            # view = movie_data['movie_details'][0]['user_views']
            year = movie_data['movie_details'][0]['year']
            time = movie_data['movie_details'][0]['time']
            tv_pg = 0
            trailer = movie_data['movie_details'][0]['trailer_url']
            PlayList.objects.get_or_create(type=film_type, name_en=title, name_fa=title, summary=summary,
                                           imdb_score=rating, is_free=False, year=year, time=time,
                                           tv_pg=tv_pg, trailer_url=trailer, thumb_image=to_url(title) + '.jpg',
                                           created_by=creator)
            m = PlayList.objects.get(name_en=title)
            m.page_url = 'movie/' + str(m.id) + '/' + to_url(title) + '/' + to_url(title)
            m.save()

            ### SEASON
            Season.objects.get_or_create(name=1, playlist=m)
            s = Season.objects.get(playlist=m)
            ### ACtor
            i = 0
            for actor in movie_data['actor_details']:
                name = movie_data['actor_details'][i]['name']
                summary = movie_data['actor_details'][i]['summary']
                Actor.objects.get_or_create(name=name, summary=summary, thumb_image=to_url(name) + '.jpg')
                a = Actor.objects.get(name=movie_data['actor_details'][i]['name'])
                m.actor.add(a)
                i += 1
            ### DIRECTOR
            try:
                dir_name = movie_data['dir_details'][0]['name']
                dir_bio = movie_data['dir_details'][0]['summary']
                Director.objects.get_or_create(name=dir_name, summary=dir_bio, thumb_image=to_url(dir_name) + '.jpg')
                d = Director.objects.get(name=movie_data['dir_details'][0]['name'])
                m.director.add(d)
                try:
                    dir2_name = movie_data['dir_details'][1]['name']
                    dir2_bio = movie_data['dir_details'][1]['bio']
                    Director.objects.get_or_create(name=dir2_name, summary=dir2_bio,
                                                   thumb_image=to_url(dir2_name) + '.jpg')
                    d2 = Director.objects.get(name=movie_data['dir_details'][1]['name'])
                    m.director.add(d2)
                except:
                    Exception('director not available')
            except:
                Exception('director not available')

            # COUNTRY
            try:
                Country.objects.get_or_create(name=movie_data['movie_details'][0]['country'])
                country = Country.objects.get(name=movie_data['movie_details'][0]['country'])
                m.country.add(country)
            except:
                Exception('could not insert country')

            ### CATEGORY
            try:
                if len(category1) > 1:
                    c1 = Category.objects.get(index=movie_data['movie_details'][0]['category1'])
                    c1.page_url = category1
                    m.category.add(c1)
            except:
                Exception('Could not innsert category')

            try:
                if len(category2) > 1:
                    c2 = Category.objects.get(index=movie_data['movie_details'][0]['category2'])
                    c2.page_url = category2
                    m.category.add(c2)
            except:
                Exception('Category 2 not inserted')
            try:
                if len(category3) > 1:
                    c3 = Category.objects.get(index=movie_data['movie_details'][0]['category3'])
                    c3.page_url = category3
                    m.category.add(c3)
            except:
                Exception('Category 3 not inserted')
            try:
                if len(category4) > 1:
                    c4 = Category.objects.get(index=movie_data['movie_details'][0]['category4'])
                    c4.page_url = category4
                    m.category.add(c4)
            except:
                Exception('Category 4 not inserted')

            ### EPISODE
            Episode.objects.get_or_create(playlist=m, season=s, stream_url='https://ss.evafilm.stream/ss-video/',
                                          download_url='https://ss.evafilm.stream/dl-video/',
                                          subtitle_vtt_url='https://ss.evafilm.stream/ss-video/',
                                          subtitle_srt_url='https://ss.evafilm.stream/ss-video/')
            ep = Episode.objects.get(playlist=m)
            ep.page_url = 'p/' + str(ep.id) + '/'
            ep.save()

        if form2.is_valid():
            movie_data, category1, category2, category3, category4, film_type = multiple_scraper(
                form2.cleaned_data['multi_url'])

            movie_i = 1
            for movie in movie_data:
                title = movie_data[movie]['movie_details'][0]['title']
                summary = movie_data[movie]['movie_details'][0]['summary']
                rating = movie_data[movie]['movie_details'][0]['rating']
                view = movie_data[movie]['movie_details'][0]['user_views']
                year = movie_data[movie]['movie_details'][0]['year']
                time = movie_data[movie]['movie_details'][0]['time']
                tv_pg = 0
                trailer = movie_data[movie]['movie_details'][0]['trailer_url']
                PlayList.objects.get_or_create(type=film_type, name_en=title, name_fa=title, summary=summary,
                                               imdb_score=rating, is_free=False, year=year, time=time,
                                               tv_pg=tv_pg, trailer_url=trailer, thumb_image=to_url(title) + '.jpg',
                                               created_by=creator)
                m = PlayList.objects.get(name_en=title)
                m.page_url = 'movie/' + str(m.id) + '/' + to_url(title) + '/' + to_url(title)
                m.save()

                ### SEASON
                Season.objects.get_or_create(name=1, playlist=m)
                s = Season.objects.get(playlist=m)
                ### ACtor
                movie_actors = 1
                actor_i = 0
                for actor in range(0, 5):
                    name = movie_data[movie]['actors'][actor_i]['name']
                    summary = movie_data[movie]['actors'][actor_i]['summary']
                    Actor.objects.get_or_create(name=name, summary=summary, thumb_image=to_url(name) + '.jpg')
                    a = Actor.objects.get(name=movie_data[movie]['actors'][actor_i]['name'])
                    m.actor.add(a)
                    actor_i += 1
                ### DIRECTOR
                try:
                    dir_name = movie_data[movie]['directors'][0]['name']
                    dir_bio = movie_data[movie]['directors'][0]['summary']
                    Director.objects.get_or_create(name=dir_name, summary=dir_bio,
                                                   thumb_image=to_url(dir_name) + '.jpg')
                    d = Director.objects.get(name=movie_data[movie][0]['name'])
                    m.director.add(d)
                    try:
                        dir2_name = movie_data[movie]['directors'][1]['name']
                        dir2_bio = movie_data[movie]['directors'][1]['bio']
                        Director.objects.get_or_create(name=dir2_name, summary=dir2_bio,
                                                       thumb_image=to_url(dir2_name) + '.jpg')
                        d2 = Director.objects.get(name=movie_data[movie]['directors'][1]['name'])
                        m.director.add(d2)
                    except:
                        Exception('director not available')
                except:
                    Exception('director not available')

                # COUNTRY
                try:
                    Country.objects.get_or_create(name=movie_data[movie]['movie_details'][0]['country'])
                    country = Country.objects.get(name=movie_data[movie]['movie_details'][0]['country'])
                    m.country.add(country)
                except:
                    Exception('could not insert country')

                ### CATEGORY
                try:
                    if len(category1) > 1:
                        c1 = Category.objects.get(index=movie_data[movie]['movie_details'][0]['category1'])
                        c1.page_url = category1
                        m.category.add(c1)
                except:
                    Exception('Could not innsert category')

                try:
                    if len(category2) > 1:
                        c2 = Category.objects.get(index=movie_data[movie]['movie_details'][0]['category2'])
                        c2.page_url = category2
                        m.category.add(c2)
                except:
                    Exception('Category 2 not inserted')
                try:
                    if len(category3) > 1:
                        c3 = Category.objects.get(index=movie_data[movie]['movie_details'][0]['category3'])
                        c3.page_url = category3
                        m.category.add(c3)
                except:
                    Exception('Category 3 not inserted')
                try:
                    if len(category4) > 1:
                        c4 = Category.objects.get(index=movie_data[movie]['movie_details'][0]['category4'])
                        c4.page_url = category4
                        m.category.add(c4)
                except:
                    Exception('Category 4 not inserted')

                ### EPISODE
                Episode.objects.get_or_create(playlist=m, season=s, stream_url='https://ss.evafilm.stream/ss-video/',
                                              download_url='https://ss.evafilm.stream/ss-video/',
                                              subtitle_vtt_url='https://ss.evafilm.stream/ss-video/',
                                              subtitle_srt_url='https://ss.evafilm.stream/ss-video/')
                ep = Episode.objects.get(playlist=m)
                ep.page_url = 'p/' + str(ep.id) + '/'
                ep.save()
                movie_actors += 1


    else:
        form = GetLinkForm()
        form2 = GetMultiLinkForm()

    qs = PlayList.objects.all()
    movie_count = qs.count()
    act_qs = Actor.objects.all()
    actor_count = act_qs.count()

    context = {
        'qs': qs,
        'movie_count': movie_count,
        'form': form,
        'form2': form2,
        'actor_count': actor_count,
    }

    return render(request, 'imdb_scraper/main.html', context)
