from django import forms
from django.forms.widgets import Textarea


class CountyPerformancePetitionForm(forms.Form):
    name = forms.CharField(
        error_messages={'required': 'You must enter a name'},
        widget=forms.TextInput(
            attrs={
                'required': 'required',
                'placeholder': 'Your name'}))
    email = forms.EmailField(
        error_messages={'required': 'You must enter a valid email address'},
        widget=forms.TextInput(
            attrs={
                'required': 'required',
                'placeholder': 'Your email address'}))

    def clean(self):
        # We want to provide a single helpful error message if both
        # name and email address aren't supplied, so override clean to
        # detect that condition
        cleaned_data = super(CountyPerformancePetitionForm,
                             self).clean()
        if not cleaned_data:
            raise forms.ValidationError(
                "You must specify a name and a valid email address")
        return cleaned_data


class CountyPerformanceSenateForm(forms.Form):
    comments = forms.CharField(
        label='Tell the senate what would like to see in your county',
        error_messages={'required': "You didn't enter a comment"},
        widget=Textarea(
            attrs={
                'rows': 5,
                'cols': 60,
                'required': 'required',
                'placeholder': 'Add any comments here'}))
