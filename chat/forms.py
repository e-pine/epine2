from django.forms import ModelForm
from django import forms
from .models import *

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'category','slug', 'start_bid_price']

        labels = {
            'category': 'Variety',
            'slug': 'Room Tag'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control',})
        self.fields['category'].widget.attrs.update({'class': 'form-control',})
        self.fields['slug'].widget.attrs.update({'class': 'form-control',})
        self.fields['start_bid_price'].widget.attrs.update({'class': 'form-control',})

class RoomFormLowQuality(forms.ModelForm):
    class Meta:
        model = RoomLowQuality
        fields = ['name', 'slug', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control',})
        self.fields['slug'].widget.attrs.update({'class': 'form-control',})

class RoomFormRejected(forms.ModelForm):
    class Meta:
        model = RoomRejected
        fields = ['name', 'slug', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control',})
        self.fields['slug'].widget.attrs.update({'class': 'form-control',})