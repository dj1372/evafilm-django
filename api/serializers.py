from rest_framework import serializers
from movies.models import PlayList, Country
from evafilm.settings import CONTENT_URL, SITE_URL


class PlaylistSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = PlayList
        fields = ('type', 'name_en', 'name_fa', 'imdb_score', 'year', 'country',  'thumb_image', 'page_url',)

    def get_type(self, obj):
        return obj.get_type_display()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret['thumb_image'] is not None:
            ret['thumb_image'] = ret['thumb_image'].replace('http', 'https')
        ret['page_url'] = SITE_URL + ret['page_url']
        country_id = ret['country'][0]
        ret['country'] = Country.objects.get(id=country_id).name
        return ret