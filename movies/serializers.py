from rest_framework import serializers
from evafilm.settings import SITE_URL
from .models import PlayList, Country, Category, Actor


class PlayListApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayList
        fields = (
            'id', 'created_at', 'updated_at', 'type', 'name_en', 'name_fa', 'category', 'imdb_score', 'year', 'country',
            'thumb_image', 'page_url',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['thumb_image'] is not None:
            ret['thumb_image'] = ret['thumb_image'].replace('http', 'https')
        ret['page_url'] = SITE_URL + str(ret['page_url'])

        ret['type'] = ret['type']

        if ret['type'] == 1:
            ret['type'] = "movie"
        elif ret['type'] == 2:
            ret['type'] = "series"
        else:
            pass

        category_array_length = len(ret['category'])
        for j in range(category_array_length):
            ret['category'][j] = Category.objects.get(id=ret['category'][j]).name_en
        else:
            pass

        country_array_length = len(ret['country'])
        for i in range(country_array_length):
            ret['country'][i] = Country.objects.get(id=ret['country'][i]).name
        else:
            pass
        return ret


class ActorApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = (
            'name', 'summary', 'thumb_image', 'page_url',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['thumb_image'] is not None:
            ret['thumb_image'] = ret['thumb_image'].replace('http', 'https')
        ret['page_url'] = SITE_URL + str(ret['page_url'])

        return ret