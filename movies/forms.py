from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'h-box-search-txt', "placeholder":"کلمه مورد نظر + اینتر" }))
