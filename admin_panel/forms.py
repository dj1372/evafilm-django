from django import forms
from movies import models as movies_models
from api import models as api_models
from django.forms.widgets import CheckboxSelectMultiple


class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = movies_models.Category
        fields = ('name_en', 'name_fa', 'page_url', 'index')


class NewActorForm(forms.ModelForm):
    class Meta:
        model = movies_models.Actor
        fields = ('name', 'summary', 'thumb_image')


class NewDirectorForm(forms.ModelForm):
    class Meta:
        model = movies_models.Director
        fields = ('name', 'summary', 'thumb_image')


class NewMovieForm(forms.ModelForm):
    class Meta:
        model = movies_models.PlayList
        fields = ('type', 'category', 'name_en', 'name_fa', 'summary', 'imdb_score',
                  'year', 'time', 'tv_pg', 'actor', 'director', 'thumb_image', 'image_1920x1080', 'image_600x810', 'country', 'is_free', 'trailer_url')

    def __init__(self, *args, **kwargs):
        super(NewMovieForm, self).__init__(*args, **kwargs)
        # self.fields['actor'].widget = CheckboxSelectMultiple()
        self.fields['actor'].queryset = movies_models.Actor.objects.all().order_by('name')
        self.fields['category'].queryset = movies_models.Category.objects.all().order_by('name_en')


class NewEpisodeForm(forms.ModelForm):
    class Meta:
        model = movies_models.Episode
        fields = ('playlist', 'season', 'index', 'title', 'summary', 'stream_url', 'download_url', 'subtitle_vtt_url',
                  'subtitle_srt_url')

#     def __init__(self, *args, **kwargs):
#         super(NewEpisodeForm, self).__init__(*args, **kwargs)
#         self.fields['server_url'].queryset = movies_models.Server.objects.filter(have_capacity=True)
    


class TimingEpisodeForm(forms.ModelForm):
    class Meta:
        model = api_models.VideoEdit
        fields = ('episode', 'titration_time', 'censor_times')


class NewSeasonForm(forms.ModelForm):
    class Meta:
        model = movies_models.Season
        fields = ('playlist', 'name')
