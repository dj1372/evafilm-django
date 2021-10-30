# from __future__ import absolute_import
from evafilm.celery import app
from imdb_scraper.models import Imdb as ImdbModel
from asyncio import Task
from movies.models import PlayList, Actor, Season, Director, Episode, Country, Category
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from PIL import Image
import re
import os
import time
import datetime
import random
import io
from django.contrib.auth import get_user_model
from celery import shared_task
import requests
import json
import celery
# from celery import task

User = get_user_model()

GENRE = ['', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
         'Fantasy', 'Film-Noir', '', 'History', 'Horror', 'Musical', '', 'Mystery', 'News', '', 'Romance', 'Sci-Fi',
         'Sport', '', 'Thriller', 'War', 'Western']

ip_addresses = [
    'http://mrrsgusd:odp5frtaq8nj@209.127.191.180:9279',
    'http://mrrsgusd:odp5frtaq8nj@193.8.56.119:9183',
    'http://mrrsgusd:odp5frtaq8nj@45.95.99.226:7786'
]



def on_success(self, retval, task_id, args, kwargs):
    obj = ImdbModel.objects.get(celery_id=task_id)
    obj.is_done = True
    obj.status = 'success'
    obj.save()


def on_failure(self, exc, task_id, args, kwargs, einfo):
    obj = ImdbModel.objects.get(celery_id=task_id)
    obj.status = 'failed'
    obj.save()


@shared_task
def movie_view(url):
    global log_var
    log_var = '----- start scraper -----'
    obj = ImdbModel.objects.filter(link=url).order_by('-id')[0]
    obj.log = log_var
    obj.save()
    creator = User.objects.get(id=1)


    movie_data, category1, category2, category3, category4, film_type = single_scraper(url)
    log_var = log_var + '\n----- end scraper -----'

    # save log
    obj = ImdbModel.objects.filter(link=url).order_by('-id')[0]
    obj.log = log_var
    obj.save()

    title = movie_data['movie_details'][0]['title']
    summary = movie_data['movie_details'][0]['summary']
    rating = movie_data['movie_details'][0]['rating']
    view = movie_data['movie_details'][0]['user_views']
    year = movie_data['movie_details'][0]['year'][:4]
    time = movie_data['movie_details'][0]['time']
    tv_pg = movie_data['movie_details'][0]['tv_pg']
    trailer = movie_data['movie_details'][0]['trailer_url']
    try:
        if len(PlayList.objects.filter(name_en__exact=title)) > 0:
            play = PlayList.objects.filter(name_en__exact=title)[0]
            play.update(name_fa=title, summary=summary,
                                    imdb_score=rating, is_free=False, year=year, time=time,
                                    tv_pg=tv_pg, trailer_url=trailer, thumb_image=to_url(title) + '.jpg',
                                    type=film_type, created_by=creator)
            log_var = log_var + '\n\n update playlist'
        else:
            PlayList.objects.create(type=film_type, name_en=title, name_fa=title, summary=summary,
                                    imdb_score=rating, is_free=False, year=year, time=time,
                                    tv_pg=tv_pg, trailer_url=trailer, thumb_image=to_url(title) + '.jpg',
                                    created_by=creator)
            log_var = log_var + '\n\n create playlist'
    except:

        log_var = log_var + '\n\n failed create or update playlist'

    obj = ImdbModel.objects.filter(link=url).order_by('-id')[0]
    obj.log = log_var
    obj.save()

    try:
        m = PlayList.objects.get(name_en=title)
        m.page_url = 'movie/' + str(m.id) + '/' + to_url(title) + '/' + to_url(title)
        m.save()
    except:
        log_var = log_var + '\n\n failed get playlist'

    obj = ImdbModel.objects.filter(link=url).order_by('-id')[0]
    obj.log = log_var
    obj.save()


    ### SEASON
    try:
        if len(Season.objects.filter(name=1, playlist=m)) > 0:
            s = Season.objects.get(playlist=m)
        else:
            s = Season.objects.create(name=1, playlist=m)
        log_var = log_var + '\n\n create or get season'
    except:
        log_var = log_var + '\n\n failed create or get season'

    obj = ImdbModel.objects.filter(link=url).order_by('-id')[0]
    obj.log = log_var
    obj.save()

    ### ACtor
    try:
        i = 0
        for actor in movie_data['actor_details']:
            name = movie_data['actor_details'][i]['name']
            summary = movie_data['actor_details'][i]['summary']
            if len(Actor.objects.filter(name=name, summary=summary)) > 0:
                a = Actor.objects.filter(name=name, summary=summary)[0]
            else:
                a = Actor.objects.create(name=name, summary=summary, thumb_image=to_url(name) + '.jpg')
                # a = Actor.objects.get(name=movie_data['actor_details'][i]['name'])
            m.actor.add(a)
            i += 1
        log_var = log_var + '\n\n create actors'
    except:
        log_var = log_var + '\n\n failed create actors'
    ### DIRECTOR
    try:
        dir_name = movie_data['dir_details'][0]['name']
        dir_bio = movie_data['dir_details'][0]['summary']
        if len(Director.objects.filter(name=dir_name, summary=dir_bio)) > 0:
            d = Director.objects.filter(name=dir_name, summary=dir_bio)[0]
        else:
            d = Director.objects.create(name=dir_name, summary=dir_bio, thumb_image=to_url(dir_name) + '.jpg')


        # Director.objects.get_or_create(name=dir_name, summary=dir_bio, thumb_image=to_url(dir_name) + '.jpg')
        # d = Director.objects.get(name=movie_data['dir_details'][0]['name'])
        m.director.add(d)
        try:
            dir2_name = movie_data['dir_details'][1]['name']
            dir2_bio = movie_data['dir_details'][1]['bio']
            if len(Director.objects.filter(name=dir2_name, summary=dir2_bio)) > 0:
                d2 = Director.objects.filter(name=dir2_name, summary=dir2_bio)[0]
            else:
                d2 = Director.objects.create(name=dir2_name, summary=dir2_bio, thumb_image=to_url(dir2_name) + '.jpg')

            # Director.objects.get_or_create(name=dir2_name, summary=dir2_bio,
            #                                thumb_image=to_url(dir2_name) + '.jpg')
            # d2 = Director.objects.get(name=movie_data['dir_details'][1]['name'])
            m.director.add(d2)
        except:
            # Exception('director not available')
            log_var = log_var + '\n\n director not available'
    except:
        # Exception('director not available')
        log_var = log_var + '\n\n director not available2'

    obj = ImdbModel.objects.filter(link=url).order_by('-id')[0]
    obj.log = log_var
    obj.save()

    # COUNTRY
    try:
        if len(Country.objects.filter(name=movie_data['movie_details'][0]['country'])) > 0:
            country = Country.objects.filter(name=movie_data['movie_details'][0]['country'])[0]
        else:
            country = Country.objects.create(name=movie_data['movie_details'][0]['country'])

        # Country.objects.get_or_create(name=movie_data['movie_details'][0]['country'])
        # country = Country.objects.get(name=movie_data['movie_details'][0]['country'])
        m.country.add(country)
    except:
        # Exception('could not insert country')
        log_var = log_var + '\n\n failed insert country'


    ### CATEGORY
    try:
        if len(category1) > 1:
            c1 = Category.objects.get(index=movie_data['movie_details'][0]['category1'])
            c1.page_url = category1
            m.category.add(c1)
    except:
        # Exception('Could not innsert category')
        log_var = log_var + '\n\n failed insert category 1'

    try:
        if len(category2) > 1:
            c2 = Category.objects.get(index=movie_data['movie_details'][0]['category2'])
            c2.page_url = category2
            m.category.add(c2)
    except:
        # Exception('Category 2 not inserted')
        log_var = log_var + '\n\n failed category 2'
    try:
        if len(category3) > 1:
            c3 = Category.objects.get(index=movie_data['movie_details'][0]['category3'])
            c3.page_url = category3
            m.category.add(c3)
    except:
        # Exception('Category 3 not inserted')
        log_var = log_var + '\n\n failed insert category 3'
    try:
        if len(category4) > 1:
            c4 = Category.objects.get(index=movie_data['movie_details'][0]['category4'])
            c4.page_url = category4
            m.category.add(c4)
    except:
        # Exception('Category 4 not inserted')
        log_var = log_var + '\n\n failed insert category 4'

    obj = ImdbModel.objects.filter(link=url).order_by('-id')[0]
    obj.log = log_var
    obj.save()

    ### EPISODE
    try:
        if len(Episode.objects.filter(playlist=m, season=s)) > 0:
            ep = Episode.objects.filter(playlist=m, season=s)[0]
        else:
            ep = Episode.objects.create(playlist=m, season=s, stream_url='https://ss.evafilm.stream/ss-video/',
                                             download_url='https://ss.evafilm.stream/dl-video/',
                                             subtitle_vtt_url='https://ss.evafilm.stream/ss-video/',
                                             subtitle_srt_url='https://ss.evafilm.stream/ss-video/')

        # Episode.objects.get_or_create(playlist=m, season=s, stream_url='https://ss.evafilm.stream/ss-video/',
        #                               download_url='https://ss.evafilm.stream/dl-video/',
        #                               subtitle_vtt_url='https://ss.evafilm.stream/ss-video/',
        #                               subtitle_srt_url='https://ss.evafilm.stream/ss-video/')
        # ep = Episode.objects.get(playlist=m)
    except:
        log_var = log_var + '\n\n failed insert episode'

    obj = ImdbModel.objects.filter(link=url).order_by('-id')[0]
    obj.log = log_var
    obj.save()
    
    ep.page_url = 'p/' + str(ep.id) + '/'
    ep.save()
    return True

def single_scraper(url):
    get_message(str(datetime.datetime.now()) + 'LOGGING STARTED')
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
        get_message('Response status: ' + str(r.status_code))
        print(r.status_code)

        soup = BeautifulSoup(r.text, 'lxml')

        try:
            title = soup.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0').text
        except:
            get_message('Title not found')
            title = None

        try:
            type_parent = soup.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-2')
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
                    dur_parent = soup.find('div', class_='TitleBlock__TitleMetaDataContainer-sc-1nlhx7j-2')
                    duration = dur_parent.find_all('li', role='presentation')[2].text
                    try:
                        dur = duration.replace("h", " ساعت و ")
                        dur = dur.replace("min", " دقیقه  ")
                    except:
                        dur = duration
                except:
                    dur = ' '
                    get_message('time not found')
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
                tv_pg = 17
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
            rating = soup.find('span', class_='iTLWoV').text
        except:
            get_message('Rating not found')
            rating = 0
        try:
            summary = soup.find('span', class_="GenresAndPlot__TextContainerBreakpointXL-cum89p-2").text
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
            category1 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-3')[0].text
            genre1 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-3')[0].text
            try:
                genre1 = GENRE.index(genre1)
            except:
                genre1 = None
                Exception('Could not set genre')
        except:
            genre1 = None
            category1 = None
            Exception('Could not set genre 1')

        try:
            category2 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-3')[1].text
            genre2 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-3')[1].text
            get_message('Fetched Genre 2')

            try:
                genre2 = GENRE.index(genre2)
            except:
                genre2 = None
                Exception('Could not set genre')

        except:
            category2 = None
            genre2 = None
            Exception('Genre 2 not found')

        try:
            category3 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-3')[2].text
            genre3 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-3')[2].text
            get_message('Fetched Genre 3')
            try:
                genre3 = GENRE.index(genre3)
            except:
                genre3 = None
                Exception('Could not set genre')

        except:
            genre3 = None
            category3 = None
            Exception('Genre 3 not found')

        try:
            category4 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-3')[3].text
            genre4 = soup.find_all('a', class_='GenresAndPlot__GenreChip-cum89p-3')[3].text
            get_message('Fetched Genre 4')
            try:
                genre4 = GENRE.index(genre4)
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
            users_view = soup.find('div', class_='AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3').text
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


def get_message(msg):
    global log_var
    log_var = log_var + '\n' + msg


# def get_message(msg):
#     with io.open('log.txt', 'a', encoding="utf-8") as logfile:
#         logfile.write(str(msg) + '\n\n')

def to_url(name):
    name = name.replace(' ', '-')
    name = name.lower()
    return name


def to_high(source):
    source = source.split('V1_')
    source = source[0] + 'V1_.jpg'
    return source
