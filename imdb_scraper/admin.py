from django.contrib import admin
from imdb_scraper.models import Imdb, ImdbScraperTest
from imdb_scraper.tasks import movie_view
from celery.result import AsyncResult
from evafilm.celery import app

from django.contrib import messages
import requests
import time
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup

class ImdbAdmin(admin.ModelAdmin):
    list_display = ['id', 'link', 'celery_id', 'status', 'is_done']
    list_filter = ['status', 'is_done']
    search_fields = ['id', 'link', 'celery_id']
    actions = ['update_status']

    def update_status(self, request, queryset):
        for data in queryset:
            if data.is_done != True:
                res = AsyncResult(str(data.celery_id), app=app)
                data.status = res.status
                if res.status == 'SUCCESS':
                    data.is_done = True
                data.save()

    update_status.short_description = "Update status"

    def save_model(self, request, obj, form, change):
        if obj.celery_id is None:
            task = movie_view.delay(obj.link)
            obj.celery_id = task.id
        else:
            pass
        super().save_model(request, obj, form, change)


admin.site.register(Imdb, ImdbAdmin)


class ImdbScraperTestAdmin(admin.ModelAdmin):
    list_display = ['id', 'test_url']
    actions = ['check_tags']

    def check_tags(self, request, queryset):
        GENRE = ['', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
                 'Fantasy', 'Film-Noir', '', 'History', 'Horror', 'Musical', '', 'Mystery', 'News', '', 'Romance', 'Sci-Fi',
                 'Sport', '', 'Thriller', 'War', 'Western']
        data = queryset[0]
        url = data.test_url
        movie_data = {
            'movie_details': [],
            'actor_details': [],
            'dir_details': [],
        }

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        main_url = 'https://www.imdb.com'
        r = requests.get(url, headers=headers)
        # time.sleep(10.4)
        if r.status_code != 200:
            messages.add_message(request, messages.ERROR, f'request failed (code:{r.status_code})')
            return None
        else:
            soup = BeautifulSoup(r.text, 'lxml')
            try:
                title = soup.find('h1', class_=data.TitleText).text
                messages.add_message(request, messages.SUCCESS, f'Title: {title}')
            except:
                messages.add_message(request, messages.ERROR, 'Title not found!')

            try:
                type_parent = soup.find('div', class_= data.TitleMetaDataContainer)
                content_type = type_parent.find_all('li', role= data.content_type_role)[0].text
                messages.add_message(request, messages.SUCCESS,f'content_type: {content_type}')
            except:
                messages.add_message(request, messages.ERROR,'Type not found!')
            try:
                if content_type == 'TV Series':
                    film_type = 2
                    dur = ' '
                    messages.add_message(request, messages.SUCCESS, f'Type: {film_type}')
                else:
                    film_type = 1
                    try:
                        dur_parent = soup.find('div', class_=data.TitleMetaDataContainer)
                        messages.add_message(request, messages.SUCCESS, f'dur_parent' )
                        duration = dur_parent.find_all('li', role=data.content_type_role)[2].text
                        messages.add_message(request, messages.SUCCESS, f'duration: {duration}')
                        try:
                            dur = duration.replace("h", " ساعت و ")
                            dur = dur.replace("min", " دقیقه  ")
                        except:
                            dur = duration
                    except:
                        dur = ' '

                        messages.add_message(request, messages.ERROR, f'time not found')

            except:
                messages.add_message(request, messages.ERROR, f'Could not set Type for this object')
                film_type = 1
                dur = ' '
                try:
                    actor_url = soup.find_all('a', class_=data.ActorName)[0].get('href')
                    r_actor = requests.get(main_url + actor_url, headers=headers).text
                    soup_actor = BeautifulSoup(r_actor, 'lxml')
                    actor_name = soup_actor.find('span', class_='itemprop').text
                    actor_bio = soup_actor.find('div', class_='inline').text
                    # movie_data['actor_details'].append({'name': actor_name, 'summary': actor_bio})
                    messages.add_message(request, messages.SUCCESS, f'actor: {actor_name}')
                    try:
                        l_actor_pic = soup_actor.find('img', id='name-poster').get('src')
                        l_actor_pic_r = requests.get(l_actor_pic, headers=headers)
                        l_actor_img = Image.open(BytesIO(l_actor_pic_r.content))
                        messages.add_message(request, messages.SUCCESS, f'Successfully saved actor image')
                    except:
                        messages.add_message(request, messages.ERROR, f'Actor image not found')
                except:
                    messages.add_message(request, messages.ERROR, f'Actor URL not found')
                    actor_name = ' '
                    actor_bio = ' '

            try:
                year = str(soup.find_all('span', class_='jedhex')[0].text)
                messages.add_message(request, messages.SUCCESS, f'Year: {year}')

            except:
                year = '0000'
                messages.add_message(request, messages.ERROR, f'Could not find Year')

            try:
                l_image_url = soup.find('img', class_='ipc-image').get('src')
                l_img_obj = requests.get(l_image_url, headers=headers)
                l_img = Image.open(BytesIO(l_img_obj.content))
                messages.add_message(request, messages.SUCCESS, f'Successfully fetched Low Quality Image')
            except:
                messages.add_message(request, messages.ERROR, f'Low quality image failed')

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
                messages.add_message(request, messages.SUCCESS, f'TV-PG: {tv_pg}')
            except:
                messages.add_message(request, messages.ERROR, f'TV-PG failed')
                tv_pg = 'R'

            try:
                rating = soup.find('span', class_=data.rating).text
                messages.add_message(request, messages.SUCCESS, f'rating: {rating}')
            except:
                messages.add_message(request, messages.ERROR, f'Rating not found')
                rating = 0
            try:
                summary = soup.find('span', class_=data.TextContainerBreakpointXL).text
                summary = summary.strip()
                messages.add_message(request, messages.SUCCESS, f'summary: {summary}')
            except:
                summary = ' '
                messages.add_message(request, messages.ERROR, f'Summary not found')

            try:
                director1 = soup.find_all('a', class_=data.director_a)[0].get('href')
                r_dir = requests.get(main_url + director1, headers=headers).text
                dir_soup = BeautifulSoup(r_dir, 'lxml')
                dir_name = dir_soup.find('span', class_='itemprop').text
                dir_bio = dir_soup.find('div', class_='inline').text
                messages.add_message(request, messages.SUCCESS, f'director: {dir_name}')
                # movie_data['dir_details'].append({'name': dir_name, 'summary': dir_bio})

                try:
                    l_dir_pic = dir_soup.find('img', id='name-poster').get('src')
                    l_dir_pic_r = requests.get(l_dir_pic, headers=headers)
                    l_dir_img = Image.open(BytesIO(l_dir_pic_r.content))
                    # l_dir_img.save('media/' + to_url(dir_name) + '.jpg')
                    messages.add_message(request, messages.SUCCESS, f'Director Low Q Image fetched')
                except:
                    messages.add_message(request, messages.ERROR, f'Director Low Q Image failed')
            except:
                director1 = ' '
                messages.add_message(request, messages.ERROR, f'No director')

            try:
                category1 = soup.find_all('a', class_=data.GenreChip)[0].text
                genre1 = soup.find_all('a', class_=data.GenreChip)[0].text
                messages.add_message(request, messages.SUCCESS, f'category and genre: {category1} | {genre1}')
                try:
                    genre1 = GENRE.index(genre1)
                    messages.add_message(request, messages.SUCCESS, f'set genre: {genre1}')
                except:
                    genre1 = None
                    messages.add_message(request, messages.ERROR, f'Could not set genre')
            except:
                genre1 = None
                category1 = None
                messages.add_message(request, messages.ERROR, f'Could not set genre 1')
            try:
                trailer = soup.find('a', class_=data.hero_media_a).get('href')
                trailer = main_url + trailer
                messages.add_message(request, messages.SUCCESS, f'trailer: {trailer}')
            except:
                trailer = ' '
                messages.add_message(request, messages.ERROR, f'failed to fetch trailer')
            try:
                users_view = soup.find('div', class_=data.TotalRatingAmount).text
                messages.add_message(request, messages.SUCCESS, f'users view: {users_view}')
            except:
                users_view = '0'
                messages.add_message(request, messages.ERROR, f'user view not found')
            try:
                c = soup.find_all('a', class_=data.country_a)
                messages.add_message(request, messages.SUCCESS, f'country: ...')
            except:
                messages.add_message(request, messages.ERROR, f'Country not found')

            # movie_data['movie_details'].append(
            #     {'title': title, 'summary': summary, 'country': country, 'rating': float(rating),
            #      'user_views': float(users_view),
            #      'year': year, 'time': dur, 'tv_pg': tv_pg, 'trailer_url': trailer, 'category1': genre1,
            #      'category2': genre2,
            #      'category3': genre3, 'category4': genre4})
            messages.add_message(request, messages.SUCCESS, f'End of the Scraping')

            # return movie_data, category1, category2, category3, category4, film_type


    check_tags.short_description = "Check Tags"


admin.site.register(ImdbScraperTest, ImdbScraperTestAdmin)
